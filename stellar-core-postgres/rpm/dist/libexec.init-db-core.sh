#!/bin/sh
# file: /usr/libexec/stellar/init-db-core

if [ -z "$PGDATA" ]; then
  echo "the script required \$PGDATA environment variable"
  exit 1
fi

if [ ! -d "$PGDATA" ]; then
  initdb --auth-host=reject --auth-local=trust --encoding=SQL_ASCII --no-locale
  cp /usr/share/stellar/postgres.4GB.cloud.conf $PGDATA/postgresql.auto.conf
fi
