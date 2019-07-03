#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4

import argparse
import requests
import re
import time
import threading
from datetime import datetime
from os import environ

# Prometheus client library
from prometheus_client import CollectorRegistry
from prometheus_client.core import Gauge, Counter
from prometheus_client.exposition import CONTENT_TYPE_LATEST, generate_latest


try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
except ImportError:
    # Python 3
    unicode = str
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn


parser = argparse.ArgumentParser(description='simple stellar-core Prometheus exporter/scraper')
parser.add_argument('--stellar-core-address', type=str,
                    help='Stellar core address. Defaults to STELLAR_CORE_ADDRESS environment '
                         'variable or if not set to http://127.0.0.1:11626',
                    default=environ.get('STELLAR_CORE_ADDRESS', 'http://127.0.0.1:11626'))
parser.add_argument('--port', type=int,
                    help='HTTP bind port. Defaults to PORT environment variable '
                         'or if not set to 9473',
                    default=int(environ.get('PORT', '9473')))
args = parser.parse_args()


class _ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """Thread per request HTTP server."""
    # Copied from prometheus client_python
    daemon_threads = True


class StellarCoreHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def get_labels(self):
        try:
            response = requests.get(self.info_url)
            json = response.json()
            build = json['info']['build']
        except Exception:
            return ['unknown', 'unknown', 'unknown', 'unknown']
        match = self.build_regex.match(build)
        build = re.sub('\s', '_', build).lower()
        build = re.sub('\(|\)', '', build)

        if not match:
            return ['unknown', 'unknown', 'unknown', build]

        labels = [
            match.group(2),
            match.group(3),
            match.group(4),
            build,
        ]
        return labels

    def duration_to_seconds(self, duration, duration_unit):
        # given duration and duration_unit, returns duration in seconds
        time_units_to_seconds = {
            'd':  'duration * 86400.0',
            'h':  'duration * 3600.0',
            'm':  'duration * 60.0',
            's':  'duration / 1.0',
            'ms': 'duration / 1000.0',
            'us': 'duration / 1000000.0',
            'ns': 'duration / 1000000000.0',
        }
        return eval(time_units_to_seconds[duration_unit])

    def set_vars(self):
        self.info_url = args.stellar_core_address + '/info'
        self.metrics_url = args.stellar_core_address + '/metrics'
        self.info_keys = ['ledger', 'peers', 'protocol_version', 'quorum', 'startedOn', 'state']
        self.ledger_metrics = {'age': 'age', 'baseFee': 'base_fee', 'baseReserve': 'base_reserve',
                               'closeTime': 'close_time', 'maxTxSetSize': 'max_tx_set_size',
                               'num': 'num', 'version': 'version'}
        self.quorum_metrics = ['agree', 'delayed', 'disagree', 'fail_at', 'missing']
        # Examples:
        #   "stellar-core 11.1.0-unstablerc2 (324c1bd61b0e9bada63e0d696d799421b00a7950)"
        #   "stellar-core 11.1.0 (324c1bd61b0e9bada63e0d696d799421b00a7950)"
        #   "v11.1.0"
        self.build_regex = re.compile('(stellar-core|v) ?(\d+)\.(\d+)\.(\d+).*$')

        self.registry = CollectorRegistry()
        self.label_names = ["ver_major", "ver_minor", "ver_patch", "build"]
        self.labels = self.get_labels()

    def error(self, code, msg):
        self.send_response(code)
        self.send_header('Content-Type', CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write('{}\n'.format(msg).encode('utf-8'))

    def do_GET(self):
        self.set_vars()
        try:
            response = requests.get(self.metrics_url)
        except requests.ConnectionError:
            self.error(504, 'Error retrieving data from {}'.format(self.metrics_url))
            return
        if not response.ok:
            self.error(504, 'Error retrieving data from {}'.format(self.metrics_url))
            return
        try:
            metrics = response.json()['metrics']
        except ValueError:
            self.error(500, 'Error parsing metrics JSON data')
            return
        # iterate over all metrics
        for k in metrics:
            metric_name = re.sub('\.|-|\s', '_', k).lower()
            metric_name = 'stellar_core_' + metric_name

            if metrics[k]['type'] == 'timer':
                # we have a timer, expose as a Prometheus Summary
                # we convert stellar-core time units to seconds, as per Prometheus best practices
                metric_name = metric_name + '_seconds'
                if 'sum' in metrics[k]:
                    # use libmedida sum value
                    total_duration = metrics[k]['sum']
                else:
                    # compute sum value
                    total_duration = (metrics[k]['mean'] * metrics[k]['count'])
                c = Counter(metric_name + '_count', 'libmedida metric type: ' + metrics[k]['type'],
                            self.label_names, registry=self.registry)
                c.labels(*self.labels).inc(metrics[k]['count'])
                s = Counter(metric_name + '_sum', 'libmedida metric type: ' + metrics[k]['type'],
                            self.label_names, registry=self.registry)
                s.labels(*self.labels).inc(self.duration_to_seconds(total_duration, metrics[k]['duration_unit']))

                # add stellar-core calculated quantiles to our summary
                summary = Gauge(metric_name, 'libmedida metric type: ' + metrics[k]['type'],
                                self.label_names + ['quantile'], registry=self.registry)
                summary.labels(*self.labels + ['0.75']).set(
                    self.duration_to_seconds(metrics[k]['75%'], metrics[k]['duration_unit']))
                summary.labels(*self.labels + ['0.99']).set(
                    self.duration_to_seconds(metrics[k]['99%'], metrics[k]['duration_unit']))
            if metrics[k]['type'] == 'histogram':
                if 'count' not in metrics[k]:
                    # Stellar-core version too old, we don't have required data
                    continue
                c = Counter(metric_name + '_count', 'libmedida metric type: ' + metrics[k]['type'],
                            self.label_names, registry=self.registry)
                c.labels(*self.labels).inc(metrics[k]['count'])
                s = Counter(metric_name + '_sum', 'libmedida metric type: ' + metrics[k]['type'],
                            self.label_names, registry=self.registry)
                s.labels(*self.labels).inc(metrics[k]['sum'])

                # add stellar-core calculated quantiles to our summary
                summary = Gauge(metric_name, 'libmedida metric type: ' + metrics[k]['type'],
                                self.label_names + ['quantile'], registry=self.registry)
                summary.labels(*self.labels + ['0.75']).set(metrics[k]['75%'])
                summary.labels(*self.labels + ['0.99']).set(metrics[k]['99%'])
            elif metrics[k]['type'] == 'counter':
                # we have a counter, this is a Prometheus Gauge
                g = Gauge(metric_name, 'libmedida metric type: ' + metrics[k]['type'], self.label_names, registry=self.registry)
                g.labels(*self.labels).set(metrics[k]['count'])
            elif metrics[k]['type'] == 'meter':
                # we have a meter, this is a Prometheus Counter
                c = Counter(metric_name, 'libmedida metric type: ' + metrics[k]['type'], self.label_names, registry=self.registry)
                c.labels(*self.labels).inc(metrics[k]['count'])

        # Export metrics from the info endpoint
        try:
            response = requests.get(self.info_url)
        except requests.ConnectionError:
            self.error(504, 'Error retrieving data from {}'.format(self.info_url))
            return
        if not response.ok:
            self.error(504, 'Error retrieving data from {}'.format(self.info_url))
            return
        try:
            info = response.json()['info']
        except ValueError:
            self.error(500, 'Error parsing info JSON data')
            return
        if not all([i in info for i in self.info_keys]):
            self.error(500, 'Error - info endpoint did not return all required fields')
            return

        # Ledger metrics
        for core_name, prom_name in self.ledger_metrics.items():
            g = Gauge('stellar_core_ledger_{}'.format(prom_name),
                      'Stellar core ledger metric name: {}'.format(core_name),
                      self.label_names, registry=self.registry)
            g.labels(*self.labels).set(info['ledger'][core_name])

        # Version 11.2.0 and later report quorum metrics in the following format:
        # "quorum" : {
        #    "qset" : {
        #      "agree": 3
        #
        # Older versions use this format:
        # "quorum" : {
        #   "758110" : {
        #     "agree" : 3,
        if 'qset' in info['quorum']:
            tmp = info['quorum']['qset']
        else:
            tmp = info['quorum'].values()[0]
        if not tmp:
            self.error(500, 'Error - missing quorum data')
            return

        for metric in self.quorum_metrics:
            g = Gauge('stellar_core_quorum_{}'.format(metric),
                      'Stellar core quorum metric: {}'.format(metric),
                      self.label_names, registry=self.registry)
            g.labels(*self.labels).set(tmp[metric])

        # Versions >=11.2.0 expose more info about quorum
        if 'transitive' in info['quorum']:
            g = Gauge('stellar_core_quorum_transitive_intersection',
                      'Stellar core quorum transitive intersection',
                      self.label_names, registry=self.registry)
            if info['quorum']['transitive']['intersection']:
                g.labels(*self.labels).set(1)
            else:
                g.labels(*self.labels).set(0)
            g = Gauge('stellar_core_quorum_transitive_last_check_ledger',
                      'Stellar core quorum transitive last_check_ledger',
                      self.label_names, registry=self.registry)
            g.labels(*self.labels).set(info['quorum']['transitive']['last_check_ledger'])
            g = Gauge('stellar_core_quorum_transitive_node_count',
                      'Stellar core quorum transitive node_count',
                      self.label_names, registry=self.registry)
            g.labels(*self.labels).set(info['quorum']['transitive']['node_count'])

        # Peers metrics
        g = Gauge('stellar_core_peers_authenticated_count',
                  'Stellar core authenticated_count count',
                  self.label_names, registry=self.registry)
        g.labels(*self.labels).set(info['peers']['authenticated_count'])
        g = Gauge('stellar_core_peers_pending_count',
                  'Stellar core pending_count count',
                  self.label_names, registry=self.registry)
        g.labels(*self.labels).set(info['peers']['pending_count'])

        g = Gauge('stellar_core_protocol_version',
                  'Stellar core protocol_version',
                  self.label_names, registry=self.registry)
        g.labels(*self.labels).set(info['protocol_version'])

        g = Gauge('stellar_core_synced', 'Stellar core sync status', self.label_names, registry=self.registry)
        if info['state'] == 'Synced!':
            g.labels(*self.labels).set(1)
        else:
            g.labels(*self.labels).set(0)

        g = Gauge('stellar_core_started_on', 'Stellar core start time in epoch', self.label_names, registry=self.registry)
        date = datetime.strptime(info['startedOn'], "%Y-%m-%dT%H:%M:%SZ")
        g.labels(*self.labels).set(int(date.strftime('%s')))

        output = generate_latest(self.registry)
        if not output:
            self.error(500, 'Error - no metrics were genereated')
            return
        self.send_response(200)
        self.send_header('Content-Type', CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(output)


if __name__ == "__main__":
    httpd = _ThreadingSimpleServer(("", args.port), StellarCoreHandler)
    t = threading.Thread(target=httpd.serve_forever)
    t.daemon = True
    t.start()
    while True:
        time.sleep(1)
