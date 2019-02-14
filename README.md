# SDF - packages

## Package based installation

If you are using Ubuntu 16.04 LTS we provide the latest stable releases of [stellar-core](https://github.com/stellar/stellar-core) and [stellar-horizon](https://github.com/stellar/go/tree/master/services/horizon) in Debian binary package format.

You may choose to install these packages individually, this offers the greatest flexibility but will require **manual** creation of the relevant configuration files and the configuration of a **PostgreSQL** database.

Alternatively you may choose to install the **stellar-quickstart** package which configures a **Testnet** `stellar-core` and `stellar-horizon` both backed by a local PostgreSQL database.

#
1. [Adding the SDF stable repository to your system](#adding-the-sdf-stable-repository-to-your-system)
2. [Quickstart](#quickstart)
3. [Installing individual packages](#installing-individual-packages)
4. [Upgrading](#upgrading)
5. [Running Horizon in production](#running-horizon-in-production)
6. [Bleeding Edge](#bleeding-edge-unstable-repository)
7. [Debug Symbols](#debug-symbols)
8. [Testnet Reset](#testnet-reset)
9. [Troubleshooting](#troubleshooting)

## Adding the SDF stable repository to your system

In order to use our repository you will need to **add our GPG public key** to your system and create a sources file.

The key we use (A136B5A6), is available from https://pgp.mit.edu with fingerprint:

**AEAF 01EE A6CA FCEF DDAE  8AA7 0463 8272 A136 B5A6**

### Download and install the public signing key:

```
wget -qO - https://apt.stellar.org/SDF.asc | sudo apt-key add -
```

### Save the repository definition to /etc/apt/sources.list.d/SDF.list:

```
echo "deb https://apt.stellar.org/public stable/" | sudo tee -a /etc/apt/sources.list.d/SDF.list
```

## Quickstart

The **stellar-quickstart** package configures a local `stellar-core` and `stellar-horizon` instance backed by a local PostgreSQL connecting to the **SDF Testnet**. Once installed you can easily modify either the `stellar-core` or `stellar-horizon` configs to suit your needs or to connect to the **SDF Pubnet** for example.

### Installation

```
# sudo apt-get update && sudo apt-get install stellar-quickstart # install packages
# stellar-core-cmd info # stellar-horizon will only start ingesting when stellar-core is in synch
```

#### Accessing the quickstart databases

The stellar-quickstart package configures 2 databases, `stellar` and `horizon`. Access to these databases is managed via the `stellar` PostgreSQL role and it's corresponding `stellar` system user.

```
# sudo -u stellar psql -d stellar
psql (9.5.10)
Type "help" for help.

stellar=> \dt
            List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+---------
 public | accountdata   | table | stellar
 public | accounts      | table | stellar
 public | ban           | table | stellar
 public | ledgerheaders | table | stellar
 public | offers        | table | stellar
 public | peers         | table | stellar
 public | publishqueue  | table | stellar
 public | pubsub        | table | stellar
 public | scphistory    | table | stellar
 public | scpquorums    | table | stellar
 public | signers       | table | stellar
 public | storestate    | table | stellar
 public | trustlines    | table | stellar
 public | txfeehistory  | table | stellar
 public | txhistory     | table | stellar
(15 rows)
```

#### stellar-core new-db

As with [accessing the database directly](#accessing-the-quickstart-databases), you can re-initialise the `stellar-core` db by running `stellar-core` as the `stellar` system user.

```
# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-db
2018-01-22T19:43:20.715 GABA2 [Database INFO] Connecting to: postgresql://dbname=stellar user=stellar
2018-01-22T19:43:20.719 GABA2 [SCP INFO] LocalNode::LocalNode@GABA2 qSet: 273af2
2018-01-22T19:43:20.833 GABA2 [Database INFO] Applying DB schema upgrade to version 2
2018-01-22T19:43:20.851 GABA2 [Database INFO] Applying DB schema upgrade to version 3
2018-01-22T19:43:20.857 GABA2 [Database INFO] Applying DB schema upgrade to version 4
2018-01-22T19:43:20.866 GABA2 [Database INFO] Applying DB schema upgrade to version 5
2018-01-22T19:43:20.872 GABA2 [default INFO] *
2018-01-22T19:43:20.872 GABA2 [default INFO] * The database has been initialized
2018-01-22T19:43:20.872 GABA2 [default INFO] *
2018-01-22T19:43:20.874 GABA2 [Ledger INFO] Established genesis ledger, closing
2018-01-22T19:43:20.874 GABA2 [Ledger INFO] Root account seed: SCXXZABQBBVSHQLXASSQU7MQSCOI56JMB24GTJGKKPUY3SYLGBASEGQ6
2018-01-22T19:43:20.879 GABA2 [default INFO] *
2018-01-22T19:43:20.879 GABA2 [default INFO] * The next launch will catchup from the network afresh.
2018-01-22T19:43:20.879 GABA2 [default INFO] *
2018-01-22T19:43:20.879 GABA2 [default INFO] Application destructing
2018-01-22T19:43:20.879 GABA2 [default INFO] Application destroyed
```

##### moving on from Quickstart

`stellar-quickstart` is a **configuration** package that through it's dependencies pulls in the required packages.

| Package                           | Dependencies                | Comments                                                                           |
|:----------------------------------|:----------------------------|:-----------------------------------------------------------------------------------|
| stellar-core                      | none                        | installs stellar-core binary, systemd service, logrotate script, documentation     |
| stellar-core-utils                | none                        | installs useful command line tools (stellar-core-cmd)                              |
| stellar-core-prometheus-exporter  | none                        | installs a Prometheus exporter to facilitate ingesting stellar-core metrics        |
| stellar-core-postgres             | stellar-core, PostgreSQL    | configures a PostgreSQL server, creates a stellar db,role and system user          |
| stellar-horizon                   | none                        | installs stellar-horizon binary, systemd service                                   |
| stellar-horizon-utils             | none                        | installs useful command line tools (stellar-horizon-cmd)                           |
| stellar-horizon-postgres          | stellar-horizon, PostgreSQL | configures a PostgreSQL server, creates a horizon db and stellar role, system user |
| stellar-quickstart                | stellar-core-postgres, stellar-horizon-postgres | pulls in required packages via it's dependencies               |

Once you are comfortable with the various packages that `stellar-quickstart` brings in as dependencies, it is possible to install them individually.

See [Running Horizon in production](#running-horizon-in-production) for a generic distributed Horizon cluster, you will need to configure **PostgreSQL** which unfortunately is out of the scope of this document.

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
      "UNSAFE_QUORUM" : "UNSAFE QUORUM ALLOWED",
      "build" : "stellar-core 0.6.4 (631687e6324a5f1bcbd92982fee3fd51fa1b80a2)",
      "ledger" : {
         "age" : 1,
         "closeTime" : 1512646297,
         "hash" : "6b01ce7ca7528632c0e2afd9387f7fddcdae7e17bc4101373c92e35b91ea0c29",
         "num" : 5822467
      },
      "network" : "Test SDF Network ; September 2015",
      "numPeers" : 3,
      "protocol_version" : 8,
      "quorum" : {
         "5822466" : {
            "agree" : 3,
            "disagree" : 0,
            "fail_at" : 2,
            "hash" : "273af2",
            "missing" : 0,
            "phase" : "EXTERNALIZE"
         }
      },
      "state" : "Synced!"
   }
}
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

## Upgrading

##### stellar-core

```
# stellar-core version
# stellar-core 10.1.0 (1fe2e8a768ecc4db2d53a4a67fc733bb1e99ecd1)
# sudo apt-get update && sudo apt-get install stellar-core
# ...
# stellar-core version
# stellar-core 10.2.0 (54504c714ab6e696283e0bd0fdf1c3a029b7c88b)
```

##### stellar-horizon

The stellar-horizon package attempts to migrate the db schema after every upgrade. It extracts database connection parameters from `/etc/default/stellar-horizon`, runs db migrations and finally restarts stellar-horizon post migration resulting in minimal downtime.

```
# stellar-horizon version                                                                                                                                              19:24:05
# v0.12.0-testing
# sudo apt-get update && sudo apt-get install stellar-horizon
# stellar-horizon-cmd db reingest # you may need to reingest manually, see changelog for details
# ...
# stellar-horizon version
# 0.12.0
```

## Running Horizon in production

Running your own distributed Horizon setup is **highly** recommended for production environments.

**reminder:** the SDF horizon cluster does not have an SLA!

How you achieve this **distributed environment** is dependent on your internal infrastructure. If possible, using managed services such as AWS (ELB,RDS,EC2) or other cloud providers will greatly simplify your environment.

Given this, the following principles should apply to most hosting environments.

 * distribute the Horizon service across multiple **load-balanced** instances (ELB,EC2)
 * only `ingest` on 1 horizon node
 * run a dedicated **non-validating** `stellar-core` instance which the Horizon cluster will connect to and ingest from
 * run a highly available [PostgreSQL cluster](https://www.postgresql.org/docs/9.5/static/high-availability.html) ( or RDS) for each of the required databases (`stellar`,`horizon`)
 * use a heartbeat ([Keepalived](https://github.com/acassen/keepalived)) to avoid `core-001` becoming a Single Point Of Failure
   * during failover the `core-db` and `stellar-core` instance accessed by Horizon need to be updated

![Generic Distributed Horizon Cluster](images/generic-distributed-horizon.png)

## Bleeding Edge Unstable Repository

If you would like to install our Release Candidates and/or track the Master branch, you can do so by using our `unstable` repository. As the name indicates this repository and it's packages are not recommended for production deployments. Use at your own risk.

### Save the `unstable` repository definition to /etc/apt/sources.list.d/SDF-unstable.list:

```
echo "deb https://apt.stellar.org/public unstable/" | sudo tee -a /etc/apt/sources.list.d/SDF-unstable.list
```

## Debug Symbols

We provide `stellar-core-dbg` packages containing the stellar-core debug symbols.

```
apt-get install stellar-core-dbg
```

## Testnet Reset

The Testnet network is reset quarterly by the Stellar Development Foundation. The exact date will be announced with at least two weeks notice on the Stellar Dashboard as well as on several of Stellar’s online developer communities.

The reset will always occur at 09:00 UTC on the announced reset date.

Post reset you will need to perform a small maintenance in order to join/synch to the new network:

#### stellar-core maintenance overview

 * stop `stellar-core`
 * clear/recreate `stellar` database
 * re-initialise `stellar`db schema
 * optionally re-init your history archives (only required if you publish your own archives)
 * start `stellar-core`

##### maintenance steps

```
# sudo systemctl stop stellar-core
# sudo -u stellar psql -c ‘DROP DATABASE stellar’`
# sudo -u stellar psql -c ‘CREATE DATABASE stellar’
# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-db
# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist ARCHIVE_NAME
# sudo systemctl start stellar-core
```

#### stellar-horizon maintenance overview

 * stop `stellar-horizon`
 * clear/recreate `horizon` database
 * re-initialise `horizon`db schema

##### maintenance steps

```
# sudo systemctl stop stellar-horizon
# sudo -u stellar psql -c ‘DROP DATABASE horizon’
# sudo -u stellar psql -c ‘CREATE DATABASE horizon’
# sudo stellar-horizon-cmd db init
# sudo systemctl stop stellar-horizon
```

## Troubleshooting

### Testnet reset known issue

We do not update the `NETWORK_PASSPHRASE` as part of the reset process, this greatly simplifies the procedure for most.

However in practice this means that it may be possible for your `stellar-core` instance to receive `stale SCP messages` from nodes still trying to connect to the previous Testnet, if this occurs your node will permanently get stuck during the initial synch as it never receives the correct `trigger` ledger to join the new network.

For the avoidance of doubt, a normal node's `Waiting for trigger ledger ETA` is counted down by 5 seconds at roughly 5 second intervals or more precisely at the rate ledgers are processed on the new network.

If your node is stuck waiting for a trigger ledger and the ETA doesn't get lower then you are likely experiencing this issue.

`Catching up: Waiting for trigger ledger: 22463254/22463297, ETA: 215s"`

If this occurs on your node, truncating the `peers` table within the `stellar` database will usually allow the instance to re-join what is hopefully the new network.

```
# sudo systemctl stop stellar-core
# sudo -u stellar psql -c 'TRUNCATE peers'
# sudo systemctl start stellar-core
```
