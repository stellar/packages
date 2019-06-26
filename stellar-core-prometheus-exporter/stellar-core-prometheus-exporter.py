#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4

import argparse
import requests
import re
import time
from datetime import datetime

# Prometheus client library
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, SummaryMetricFamily, REGISTRY

parser = argparse.ArgumentParser(description='simple stellar-core Prometheus exporter/scraper')
parser.add_argument('--uri', type=str,
                    help='core metrics uri, default: http://127.0.0.1:11626/metrics',
                    default='http://127.0.0.1:11626/metrics')
parser.add_argument('--info-uri', type=str,
                    help='info endpoint uri, default: http://127.0.0.1:11626/info',
                    default='http://127.0.0.1:11626/info')
parser.add_argument('--port', type=int,
                    help='HTTP bind port, default: 9473',
                    default=9473)
args = parser.parse_args()


# given duration and duration_unit, returns duration in seconds
def duration_to_seconds(duration, duration_unit):
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


class StellarCoreCollector(object):
    def __init__(self):
        self.info_keys = ['ledger', 'peers', 'protocol_version', 'quorum', 'startedOn', 'state']
        self.ledger_metrics = {'age': 'age', 'baseFee': 'base_fee', 'baseReserve': 'base_reserve',
                               'closeTime': 'close_time', 'maxTxSetSize': 'max_tx_set_size',
                               'num': 'num', 'version': 'version'}
        self.quorum_metrics = ['agree', 'delayed', 'disagree', 'fail_at', 'missing']
        # Examples:
        #   "stellar-core 11.1.0-unstablerc2 (324c1bd61b0e9bada63e0d696d799421b00a7950)"
        #   "stellar-core 11.1.0 (324c1bd61b0e9bada63e0d696d799421b00a7950)"
        #   "v11.1.0"
        self.build_regex = re.compile('(stellar-core|v) ?(\d+)\.(\d+)\.(\d+)(-[^ ]+)?.*$')

    def get_labels(self):
        try:
            response = requests.get(args.info_uri)
            json = response.json()
            build = json['info']['build']
        except Exception:
            return {}
        match = self.build_regex.match(build)
        if not match:
            return {}

        if not match.group(5):
            ver_extra = ''  # If regex did not match ver_extra set it to empty string
        else:
            ver_extra = match.group(5).lstrip('-')

        labels = {
            "ver_major": match.group(2),
            "ver_minor": match.group(3),
            "ver_patch": match.group(4),
            "ver_extra": ver_extra,
        }
        return labels

    def collect(self):
        # TODO handle missing labels, probably return 500?
        labels = self.get_labels()
        labels_p75 = labels.copy()  # Work on copy of labels variable to avoid other metrics getting quantile label
        labels_p75.update({'quantile': '0.75'})
        labels_p99 = labels.copy()  # Work on copy of labels variable to avoid other metrics getting quantile label
        labels_p99.update({'quantile': '0.99'})

        response = requests.get(args.uri)
        metrics = response.json()['metrics']
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
                summary = SummaryMetricFamily(metric_name, 'libmedida metric type: ' + metrics[k]['type'], labels=labels.keys())
                summary.add_metric(labels.values(), count_value=metrics[k]['count'],
                                   sum_value=(duration_to_seconds(total_duration, metrics[k]['duration_unit'])))
                # add stellar-core calculated quantiles to our summary
                summary.add_sample(metric_name, labels=labels_p75,
                                   value=(duration_to_seconds(metrics[k]['75%'], metrics[k]['duration_unit'])))
                summary.add_sample(metric_name, labels=labels_p99,
                                   value=(duration_to_seconds(metrics[k]['99%'], metrics[k]['duration_unit'])))
                yield summary
            elif metrics[k]['type'] == 'counter':
                # we have a counter, this is a Prometheus Gauge
                g = GaugeMetricFamily(metric_name, 'libmedida metric type: ' + metrics[k]['type'], labels=labels.keys())
                g.add_metric(labels.values(), metrics[k]['count'])
                yield g
            elif metrics[k]['type'] == 'meter':
                # we have a meter, this is a Prometheus Counter
                c = CounterMetricFamily(metric_name, 'libmedida metric type: ' + metrics[k]['type'], labels=labels.keys())
                c.add_metric(labels.values(), metrics[k]['count'])
                yield c

        # Export metrics from the info endpoint
        response = requests.get(args.info_uri)
        info = response.json()['info']
        if not all([i in info for i in self.info_keys]):
            print('WARNING: info endpoint did not return all required fields')
            return

        # Ledger metrics
        for core_name, prom_name in self.ledger_metrics.items():
            g = GaugeMetricFamily('stellar_core_ledger_{}'.format(prom_name),
                                  'Stellar core ledger metric name: {}'.format(core_name),
                                  labels=labels.keys())
            g.add_metric(labels.values(), info['ledger'][core_name])
            yield g

        # Quorum metrics are reported under dynamic name for example:
        # "quorum" : {
        #   "758110" : {
        #     "agree" : 3,
        tmp = info['quorum'].values()[0]
        for metric in self.quorum_metrics:
            g = GaugeMetricFamily('stellar_core_quorum_{}'.format(metric),
                                  'Stellar core quorum metric: {}'.format(metric),
                                  labels=labels.keys())
            g.add_metric(labels.values(), tmp[metric])
            yield g

        # Peers metrics
        g = GaugeMetricFamily('stellar_core_peers_authenticated_count',
                              'Stellar core authenticated_count count',
                              labels=labels.keys())
        g.add_metric(labels.values(), info['peers']['authenticated_count'])
        yield g
        g = GaugeMetricFamily('stellar_core_peers_pending_count',
                              'Stellar core pending_count count',
                              labels=labels.keys())
        g.add_metric(labels.values(), info['peers']['pending_count'])
        yield g

        g = GaugeMetricFamily('stellar_core_protocol_version',
                              'Stellar core protocol_version',
                              labels=labels.keys())
        g.add_metric(labels.values(), info['protocol_version'])
        yield g

        g = GaugeMetricFamily('stellar_core_synced', 'Stellar core sync status', labels=labels.keys())
        if info['state'] == 'Synced!':
            g.add_metric(labels.values(), 1)
        else:
            g.add_metric(labels.values(), 0)
        yield g

        g = GaugeMetricFamily('stellar_core_started_on', 'Stellar core start time in epoch', labels=labels.keys())
        date = datetime.strptime(info['startedOn'], "%Y-%m-%dT%H:%M:%SZ")
        g.add_metric(labels.values(), int(date.strftime('%s')))
        yield g


if __name__ == "__main__":
    REGISTRY.register(StellarCoreCollector())
    start_http_server(args.port)
    while True:
        time.sleep(1)
