#!/usr/bin/python

import argparse
import requests
import json
import re
import time

# Prometheus client library
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, SummaryMetricFamily, REGISTRY

parser = argparse.ArgumentParser(description='simple stellar-core Prometheus exporter/scraper')
parser.add_argument('--uri', type=str,
                    help='core metrics uri, default: http://127.0.0.1:11626/metrics',
                    default='http://127.0.0.1:11626/metrics')
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
  def collect(self):
    response = requests.get(args.uri)
    json = response.json()

    metrics   = json['metrics']

    # iterate over all metrics
    for k in metrics:
      underscores = re.sub('\.|-|\s', '_', k).lower()

      if metrics[k]['type'] == 'timer':
        # we have a timer, expose as a Prometheus Summary
        # we convert stellar-core time units to seconds, as per Prometheus best practices
        underscores = underscores + '_seconds'
        if 'sum' in metrics[k]:
          # use libmedida sum value
          total_duration = metrics[k]['sum']
        else:
          # compute sum value
          total_duration = (metrics[k]['mean'] * metrics[k]['count'])
        summary = SummaryMetricFamily(underscores, 'libmedida metric type: ' + metrics[k]['type'], count_value=metrics[k]['count'], sum_value=(duration_to_seconds(total_duration, metrics[k]['duration_unit'])))
        # add stellar-core calculated quantiles to our summary
        summary.add_sample(underscores, labels={'quantile':'0.75'}, value=(duration_to_seconds(metrics[k]['75%'], metrics[k]['duration_unit'])))
        summary.add_sample(underscores, labels={'quantile':'0.99'}, value=(duration_to_seconds(metrics[k]['99%'], metrics[k]['duration_unit'])))
        yield summary
      elif metrics[k]['type'] == 'counter':
        # we have a counter, this is a Prometheus Gauge
        yield GaugeMetricFamily(underscores, 'libmedida metric type: ' + metrics[k]['type'], value=metrics[k]['count'])
      elif metrics[k]['type'] == 'meter':
        # we have a meter, this is a Prometheus Counter
        yield CounterMetricFamily(underscores, 'libmedida metric type: ' + metrics[k]['type'], value=metrics[k]['count'])

if __name__ == "__main__":
  REGISTRY.register(StellarCoreCollector())
  start_http_server(args.port)
  while True: time.sleep(1)
