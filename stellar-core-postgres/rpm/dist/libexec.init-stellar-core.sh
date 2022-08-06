#!/bin/sh
# file: /usr/libexec/stellar/init-stellar-core

if [ -z "$STELLAR_CONFIG_PATH" ]; then
  echo "the script required \$STELLAR_CONFIG_PATH environment variable"
  exit 1
fi

if [ ! -d "buckets" ]; then
  createdb --host=/var/run/stellar core
  stellar-core --conf ${STELLAR_CONFIG_PATH} new-db
  stellar-core --conf ${STELLAR_CONFIG_PATH} new-hist local ||:
fi
