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
        summary = SummaryMetricFamily(underscores, 'libmedida metric type: ' + metrics[k]['type'], count_value=metrics[k]['count'], sum_value=(metrics[k]['mean_rate'] * metrics[k]['count']))
        # add stellar-core calculated quantiles to our summary
        summary.add_sample(underscores, labels={'quantile':'0.75'}, value=metrics[k]['75%']) 
        summary.add_sample(underscores, labels={'quantile':'0.95'}, value=metrics[k]['95%'])
        summary.add_sample(underscores, labels={'quantile':'0.98'}, value=metrics[k]['98%']) 
        summary.add_sample(underscores, labels={'quantile':'0.99'}, value=metrics[k]['99%']) 
        summary.add_sample(underscores, labels={'quantile':'0.999'}, value=metrics[k]['99.9%']) 
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
