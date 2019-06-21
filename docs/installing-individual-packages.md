#  SDF - packages

1.  [Adding the SDF stable repository to your system](adding-the-sdf-stable-repository-to-your-system.md)
2.  [Quickstart](quickstart.md)
3.  [Installing individual packages](installing-individual-packages.md)
4.  [Upgrading](upgrading.md)
5.  [Bleeding Edge](bleeding-edge-unstable-repository.md)
6.  [Debug Symbols](debug-symbols.md)
7.  [Running Horizon in production](running-horizon-in-production.md)
8.  [Building Packages](building-packages.md)
9.  [Publishing a History archive](publishing-a-history-archive.md)
10. [Testnet Reset](testnet-reset.md)

## Installing individual packages

If you choose to install the individual packages, you will need to install your own configuration files as none are provided by default, you will also need to configure PostgreSQL as well as create users and relevant databases.

* **stellar-core:** is configured by modifying `/etc/stellar/stellar-core.cfg`
* **stellar-horizon:** is configured by modifying `/etc/default/stellar-horizon`

### Installation

**Recent stellar-core packages now start the service post installation**, if you would like to retain the previous behaviour and prevent stellar-core from starting automatically, you could use `systemctl mask`.

#### masking the service

if the package is already installed:

```
systemctl mask stellar-core # no start post upgrades
```

if the package is not yet installed:

```
ln -s /dev/null /etc/systemd/system/stellar-core.service # no start post installation
```

#### installing

* `apt-get update && apt-get install stellar-core` or `apt-get update && apt-get install stellar-horizon`
* deploy suitable configs, see [docs](https://www.stellar.org/developers/software/)
* `systemctl start stellar-core` or `systemctl start stellar-horizon`

##### Systemd Unit

For convenience our packages install Systemd services `/lib/systemd/system/stellar-core.service` or `/lib/systemd/system/stellar-horizon.service`. These services are enabled and started by default.

```
systemctl start stellar-core
systemctl status
● stellar-core.service - SDF - stellar-core
   Loaded: loaded (/lib/systemd/system/stellar-core.service; enabled; vendor preset: enabled)
   Active: active (running) since Wed 2018-03-21 12:01:05 UTC; 1min 46s ago
 Main PID: 1522 (stellar-core)
    Tasks: 4
   Memory: 4.7M
      CPU: 437ms
   CGroup: /system.slice/stellar-core.service
           └─1522 /usr/bin/stellar-core --conf /etc/stellar/stellar-core.cfg run
```

##### Logrotate

The stellar-core Debian package installs a Logrotate script under `/etc/logrotate.d/stellar-core`.

Due to the way stellar-core currently manages it's logs, we are temporarily using `copytruncate` to rotate the logs. Unfortunately, a minimal amount of log entries may be lost with this setup. We are actively looking at ways of improving this.

You can disable automatic logrotation `rm /etc/logrotate.d/stellar-core`

```
/var/log/stellar/*.log {
  daily
  missingok
  rotate 14
  compress
  notifempty
  copytruncate
  create 0640 stellar stellar
}
```

##### stellar-core-cmd

This simple script wraps a curl call to the stellar-core http endpoint.

```json
stellar-core-cmd info
{
   "info" : {
      "build" : "stellar-core 10.2.0 (54504c714ab6e696283e0bd0fdf1c3a029b7c88b)",
      "history_failure_rate" : "0",
      "ledger" : {
         "age" : 10,
         "baseFee" : 100,
         "baseReserve" : 5000000,
         "closeTime" : 1550142213,
         "hash" : "95b9b72407174e9d79f184f19b48a0c0a4348573d425f1327191c89fbe2e8235",
         "maxTxSetSize" : 100,
         "num" : 2227691,
         "version" : 10
      },
      "network" : "Test SDF Network ; September 2015",
      "peers" : {
         "authenticated_count" : 3,
         "pending_count" : 3
      },
      "protocol_version" : 10,
      "quorum" : {
         "2227691" : {
            "agree" : 3,
            "delayed" : 0,
            "disagree" : 0,
            "fail_at" : 2,
            "hash" : "273af2",
            "missing" : 0,
            "phase" : "EXTERNALIZE"
         }
      },
      "startedOn" : "2019-02-14T10:41:29Z",
      "state" : "Synced!"
   }
}
```

##### stellar-core-gap-detect

Simple script that queries the `stellar` database and checks for gaps in the ledgerheaders.

```
# stellar-core-gap-detect
 gap_start | gap_end
-----------+----------
  23547277 | 23782142
(1 row)
```

##### stellar-horizon-cmd

This simple script exports all variables found in /etc/default/stellar-horizon and wraps stellar-horizon.

```
stellar-horizon-cmd db reingest
INFO[0000] reingest: all                                 end=7888983 pid=26862 start=7888985
INFO[0000] ingest: range complete                        end=7888983 err=<nil> ingested=3 pid=26862 start=7888985
INFO[0000] reingest: complete                            count=3 means="load: 2.138432ms clear: 525.499µs ingest: 525.499µs" pid=26862 rate=111.0815757543577
```

##### Debian

We do not currently test the packages on Debian GNU/Linux as part of our internal release process.

That said, the packages install correctly on Debian Stretch although you will need to add the official PostgreSQL apt repository to satisfy dependencies, instructions can be found in the [PostgreSQL APT documentation](https://wiki.postgresql.org/wiki/Apt#Quickstart).

##### User permissions

We create and make extensive use of a `stellar` user during the installation, runtime, upgrade process'. With this in mind, the `stellar` user needs r/w access to the stellar-core buckets directory (/var/lib/stellar/buckets) and to the log directory (/var/log/stellar/).

If you need to use different mount points, you will need to make sure the `stellar` user has r/w access.
