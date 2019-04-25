# SDF - packages

## Package based installation

If you are using Ubuntu 16.04 LTS we provide the latest stable releases of [stellar-core](https://github.com/stellar/stellar-core) and [stellar-horizon](https://github.com/stellar/go/tree/master/services/horizon) in Debian binary package format.

You may choose to install these packages individually, this offers the greatest flexibility but will require **manual** creation of the relevant configuration files and the configuration of a **PostgreSQL** database.

Alternatively you may choose to install the **stellar-quickstart** package which configures a **Testnet** `stellar-core` and `stellar-horizon` both backed by a local PostgreSQL database.

#
1.  [Adding the SDF stable repository to your system](#adding-the-sdf-stable-repository-to-your-system)
2.  [Quickstart](#quickstart)
3.  [Installing individual packages](#installing-individual-packages)
4.  [Upgrading](#upgrading)
5.  [Running Horizon in production](#running-horizon-in-production)
6.  [Bleeding Edge](#bleeding-edge-unstable-repository)
7.  [Building Packages](#building-packages)
8.  [Debug Symbols](#debug-symbols)
9.  [Publishing a History archive](#publishing-a-history-archive)
10. [Testnet Reset](#testnet-reset)
11. [Troubleshooting](#troubleshooting)

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
## Building Packages

### stellar-core

#### dpkg-buildflags

`dpkg-buildflags` is a standard component of the Debian packaging system, when called it returns system wide defaults for compiler flags and is used primarily by the `dpkg-buildpackage` program to configure the build environment.

On Ubuntu 16.04 these default to:

```
# dpkg-buildflags | egrep '^(C|CPP|CXX|LD)FLAGS'
CFLAGS=-g -O2 -fstack-protector-strong -Wformat -Werror=format-security
CPPFLAGS=-Wdate-time -D_FORTIFY_SOURCE=2
CXXFLAGS=-g -O2 -fstack-protector-strong -Wformat -Werror=format-security
LDFLAGS=-Wl,-Bsymbolic-functions -Wl,-z,relro
```

When building the `stellar-core` packages, it is possible to override the compiler flags returned by `dpkg-buildflags` by setting certain variables in your build environment.

##### CXXFLAGS

If you need to modify to the c++ compiler flags, you may do so by setting `DEB_CXXFLAGS_SET` in your build environment which overrides the default `CXXFLAGS` value returned to `dpkg-buildpackage` by `dpkg-buildflags`.

One caveat to this which is not immediately obvious, is that we prepend `-stdlib=libc++ -fno-omit-frame-pointer -isystem /usr/include/libcxxabi` to the beginning of `DEB_CXXFLAGS_SET` or by default to the value returned by `dpkg-buildflags`.
We do this by setting `DEB_CXXFLAGS_MAINT_PREPEND` in the `debian/rules` make file to enforce the use of `clang++`,`libc++` and `libc++abi` during compilation.

Example:

```
DEB_CXXFLAGS_MAINT_PREPEND = -stdlib=libc++ -fno-omit-frame-pointer -isystem /usr/include/libcxxabi
CXXFLAGS = $(DEB_CXXFLAGS_MAINT_PREPEND) + $(DEB_CXXFLAGS_SET)
```

##### CFLAGS

If you need to modify the c compiler flags, you may do so by setting `DEB_CFLAGS_SET` in your build environment which overrides the default `CFLAGS` value returned to `dpkg-buildpackage` by `dpkg-buildflags`.

Example: 

`CFLAGS = $(DEB_CFLAGS_SET)`

##### DEB_CONFIGURE_OPTS

If you need to modify the configure script parameters you may do so by setting `DEB_CONFIGURE_OPTS` in your build environment. This overrides the default value set within the stellar-core `debian/rules`

Example:

```
# set DEB_CONFIGURE_OPTS in your environment to override
DEB_CONFIGURE_OPTS ?= --prefix=/usr --includedir=/usr/include --mandir=/usr/share/man --infodir=/usr/share/info --sysconfdir=/etc --localstatedir=/var
./configure $(DEB_CONFIGURE_OPTS)
```

##### LDFLAGS, CPPFLAGS

The methods we use above for overriding `CFLAGS` can also be used to set other variables that `dpkg-buildflags` returns.

Example:

`LDFLAGS = $(DEB_LDFLAGS_SET)`
`CPPFLAGS = $(DEB_CPPFLAGS_SET)`

## Debug Symbols

We provide `stellar-core-dbg` packages containing the stellar-core debug symbols.

```
apt-get install stellar-core-dbg
```

## Publishing a history archive

Running a full validator requires publishing the validator's history archive, this can be achieved using blob stores such as Amazon's s3, digital ocean's spaces or simply by serving a local archive directly via an HTTP server such as Nginx or Apache. Which ever method you choose to use you may find the below tips useful.

In order to publish a history archive it is essential to have a stellar-core instance running as either an [Archiver](https://www.stellar.org/developers/stellar-core/software/admin.html#archiver-nodes) or a [Full Validator](https://www.stellar.org/developers/stellar-core/software/admin.html#full-validators)

### Caching and History Archives

It is possible to significantly reduce the data transfer costs associated with running a public History archive by using common caching techniques or a CDN.

Which ever solution you choose, 3 simple rules apply to caching the History archives:

  * Do not cache the archive state file `.well-known/history-stellar.json` (**"Cache-Control: no-cache"**)
  * Do not cache HTTP 4xx responses (**"Cache-Control: no-cache"**)
  * Cache everything else for as long as possible (**> 1 day**)

### Local history archive published using nginx

 * add a history configuration stanza to your `/etc/stellar/stellar-core.cfg`:

```
[HISTORY.local]
get="cp /mnt/xvdf/stellar-core-archive/node_001/{0} {1}"
put="cp {0} /mnt/xvdf/stellar-core-archive/node_001/{1}"
mkdir="mkdir -p /mnt/xvdf/stellar-core-archive/node_001/{0}"
```

 * run new-hist to create the local archive

`# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist local`

This command creates the History archive structure:

```
# tree -a /mnt/xvdf/stellar-core-archive/
/mnt/xvdf/stellar-core-archive
└── node_001
    ├── history
    │   └── 00
    │       └── 00
    │           └── 00
    │               └── history-00000000.json
    └── .well-known
        └── stellar-history.json

6 directories, 2 file
```

 * configure a virtual host to serve the local archive (Nginx)

```
server {
  listen 80;
  root /mnt/xvdf/stellar-core-archive/node_001/;

  server_name history.example.com;

  # default is to deny all
  location / { deny all; }

  # do not cache 404 errors
  error_page 404 /404.html;
  location = /404.html {
    add_header Cache-Control "no-cache" always;
  }

  # do not cache history state file
  location ~ ^/.well-known/stellar-history.json$ {
    add_header Cache-Control "no-cache" always;
    try_files $uri;
  }

  # cache entire history archive for 1 day
  location / {
    add_header Cache-Control "max-age=86400";
    try_files $uri;
  }
}
```

### Amazon S3 backed history archive

 * add a history configuration stanza to your `/etc/stellar/stellar-core.cfg`:

```
[HISTORY.s3]
get='curl -sf http://history.example.com/{0} -o {1}' # Cached HTTP endpoint
put='aws s3 cp --region us-east-1 {0} s3://bucket.name/{1}' # Direct S3 access
```

 * run new-hist to create the s3 archive

`# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist s3`

 * serve the archive using an Amazon S3 static site
 * optionally place a reverse proxy and CDN in front of the S3 static site

```
server {
  listen 80;
  root /srv/nginx/history.example.com;
  index index.html index.htm;

  server_name history.example.com;

  # use google nameservers for lookups
  resolver 8.8.8.8 8.8.4.4;

  # bucket.name s3 static site endpoint
  set $s3_bucket "bucket.name.s3-website-us-east-1.amazonaws.com";

  # default is to deny all
  location / { deny all; }

  # do not cache 404 errors
  error_page 404 /404.html;
  location = /404.html {
    add_header Cache-Control "no-cache" always;
  }

  # do not cache history state file
  location ~ ^/.well-known/stellar-history.json$ {
    add_header Cache-Control "no-cache" always;
    proxy_intercept_errors on;
    proxy_pass  http://$s3_bucket;
    proxy_read_timeout 120s;
    proxy_redirect off;
    proxy_buffering off;
    proxy_set_header        Host            $s3_bucket;
    proxy_set_header        X-Real-IP       $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;
  }

  # cache history archive for 1 day
  location / {
    add_header Cache-Control "max-age=86400";
    proxy_intercept_errors on;
    proxy_pass  http://$s3_bucket;
    proxy_read_timeout 120s;
    proxy_redirect off;
    proxy_buffering off;
    proxy_set_header        Host            $s3_bucket;
    proxy_set_header        X-Real-IP       $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;
  }
}
```

### Before or After

#### Before

Given the choice, it is best to configure the History archive prior to your nodes initial synch to the network, this way your validator or archiver's History is published as you join/synch to the network.

#### After

If unfortunately you have not published an archive during the node's initial synch, it is still possible to use the [stellar-archivist](https://github.com/stellar/go/tree/master/tools/stellar-archivist) command line tool to mirror, scan and repair existing archives.

The steps required to create a History archive for an existing validator (ie: basic validator -> full validator) are straightforward:

 * stop your stellar-core instance (`systemctl stop stellar-core`)
 * configure a History archive for the new node

```
[HISTORY.local]
get="cp /mnt/xvdf/stellar-core-archive/node_001/{0} {1}"
put="cp {0} /mnt/xvdf/stellar-core-archive/node_001/{1}"
mkdir="mkdir -p /mnt/xvdf/stellar-core-archive/node_001/{0}"
```

 * run new-hist to create the local archive

`# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist local`

This command creates the History archive structure:

```
# tree -a /mnt/xvdf/stellar-core-archive/
/mnt/xvdf/stellar-core-archive
└── node_001
    ├── history
    │   └── 00
    │       └── 00
    │           └── 00
    │               └── history-00000000.json
    └── .well-known
        └── stellar-history.json

6 directories, 2 file
```
 * start your stellar-core instance (`systemctl start stellar-core`)
 * allow your node to join the network and start publishing a few checkpoints to the newly created archive

At this stage it is possible to use `stellar-archivist` to verify the state and integrity of your archive

```
# stellar-archivist scan file:///mnt/xvdf/stellar-core-archive/node_001
2019/04/25 11:42:51 Scanning checkpoint files in range: [0x0000003f, 0x0000417f]
2019/04/25 11:42:51 Checkpoint files scanned with 324 errors
2019/04/25 11:42:51 Archive: 3 history, 2 ledger, 2 transactions, 2 results, 2 scp
2019/04/25 11:42:51 Scanning all buckets, and those referenced by range
2019/04/25 11:42:51 Archive: 30 buckets total, 30 referenced
2019/04/25 11:42:51 Examining checkpoint files for gaps
2019/04/25 11:42:51 Examining buckets referenced by checkpoints
2019/04/25 11:42:51 Missing history (260): [0x0000003f-0x000040ff]
2019/04/25 11:42:51 Missing ledger (260): [0x0000003f-0x000040ff]
2019/04/25 11:42:51 Missing transactions (260): [0x0000003f-0x000040ff]
2019/04/25 11:42:51 Missing results (260): [0x0000003f-0x000040ff]
2019/04/25 11:42:51 No missing buckets referenced in range [0x0000003f, 0x0000417f]
2019/04/25 11:42:51 324 errors scanning checkpoints
```

As you can tell from the output of the `scan` command some history, ledger, transactions, results are missing from the local history archive

You can now repair the missing data using stellar-archivist's `repair` command and a known full archive such as the SDF public history archive

`# stellar-archivist repair http://history.stellar.org/prd/core-testnet/core_testnet_001/ file:///mnt/xvdf/stellar-core-archive/node_001/`

```
2019/04/25 11:50:15 repairing http://history.stellar.org/prd/core-testnet/core_testnet_001/ -> file:///mnt/xvdf/stellar-core-archive/node_001/
2019/04/25 11:50:15 Starting scan for repair
2019/04/25 11:50:15 Scanning checkpoint files in range: [0x0000003f, 0x000041bf]
2019/04/25 11:50:15 Checkpoint files scanned with 244 errors
2019/04/25 11:50:15 Archive: 4 history, 3 ledger, 263 transactions, 61 results, 3 scp
2019/04/25 11:50:15 Error: 244 errors scanning checkpoints
2019/04/25 11:50:15 Examining checkpoint files for gaps
2019/04/25 11:50:15 Repairing history/00/00/00/history-0000003f.json
2019/04/25 11:50:15 Repairing history/00/00/00/history-0000007f.json
2019/04/25 11:50:15 Repairing history/00/00/00/history-000000bf.json
...
2019/04/25 11:50:22 Repairing ledger/00/00/00/ledger-0000003f.xdr.gz
2019/04/25 11:50:23 Repairing ledger/00/00/00/ledger-0000007f.xdr.gz
2019/04/25 11:50:23 Repairing ledger/00/00/00/ledger-000000bf.xdr.gz
...
2019/04/25 11:51:18 Repairing results/00/00/0e/results-00000ebf.xdr.gz
2019/04/25 11:51:18 Repairing results/00/00/0e/results-00000eff.xdr.gz
2019/04/25 11:51:19 Repairing results/00/00/0f/results-00000f3f.xdr.gz
...
2019/04/25 11:51:39 Repairing scp/00/00/00/scp-0000003f.xdr.gz
2019/04/25 11:51:39 Repairing scp/00/00/00/scp-0000007f.xdr.gz
2019/04/25 11:51:39 Repairing scp/00/00/00/scp-000000bf.xdr.gz
...
2019/04/25 11:51:50 Re-running checkpoing-file scan, for bucket repair
2019/04/25 11:51:50 Scanning checkpoint files in range: [0x0000003f, 0x000041bf]
2019/04/25 11:51:50 Checkpoint files scanned with 5 errors
2019/04/25 11:51:50 Archive: 264 history, 263 ledger, 263 transactions, 263 results, 241 scp
2019/04/25 11:51:50 Error: 5 errors scanning checkpoints
2019/04/25 11:51:50 Scanning all buckets, and those referenced by range
2019/04/25 11:51:50 Archive: 40 buckets total, 2478 referenced
2019/04/25 11:51:50 Examining buckets referenced by checkpoints
2019/04/25 11:51:50 Repairing bucket/57/18/d4/bucket-5718d412bdc19084dafeb7e1852cf06f454392df627e1ec056c8b756263a47f1.xdr.gz
2019/04/25 11:51:50 Repairing bucket/8a/a1/62/bucket-8aa1624cc44aa02609366fe6038ffc5309698d4ba8212ef9c0d89dc1f2c73033.xdr.gz
2019/04/25 11:51:50 Repairing bucket/30/82/6a/bucket-30826a8569cb6b178526ddba71b995c612128439f090f371b6bf70fe8cf7ec24.xdr.gz
...
```

A final scan of the local archive confirms that it has been successfully repaired

`# stellar-archivist scan file:///mnt/xvdf/stellar-core-archive/node_001`

```
2019/04/25 12:15:41 Scanning checkpoint files in range: [0x0000003f, 0x000041bf]
2019/04/25 12:15:41 Archive: 264 history, 263 ledger, 263 transactions, 263 results, 241 scp
2019/04/25 12:15:41 Scanning all buckets, and those referenced by range
2019/04/25 12:15:41 Archive: 2478 buckets total, 2478 referenced
2019/04/25 12:15:41 Examining checkpoint files for gaps
2019/04/25 12:15:41 Examining buckets referenced by checkpoints
2019/04/25 12:15:41 No checkpoint files missing in range [0x0000003f, 0x000041bf]
2019/04/25 12:15:41 No missing buckets referenced in range [0x0000003f, 0x000041bf]
```

  * start your stellar-core instance (`systemctl start stellar-core`)

You should now have a complete history archive being written to by your full validator

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
# sudo -u stellar psql -c 'DROP DATABASE stellar' postgres
# sudo -u stellar psql -c 'CREATE DATABASE stellar' postgres
# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-db
# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist ARCHIVE_NAME
# sudo systemctl start stellar-core
```

#### stellar-horizon maintenance overview

 * stop `stellar-horizon`
 * clear/recreate `horizon` database
 * re-initialise `horizon`db schema
 * start `stellar-horizon`

##### maintenance steps

```
# sudo systemctl stop stellar-horizon
# sudo -u stellar psql -c 'DROP DATABASE horizon'
# sudo -u stellar psql -c 'CREATE DATABASE horizon'
# sudo stellar-horizon-cmd db init
# sudo systemctl start stellar-horizon
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

If your attempt at re-joining the network is still not successful then you can temporarily set `PREFERRED_PEERS_ONLY=true` which will force stellar-core to only connect to your `PREFERRED_PEERS`, hopefully allowing you to connect to an available free slot.

```
# Only connect to the SDF Testnet validators temporarily
# remove PREFERRED_PEERS_ONLY=true once connected to the new network
PREFERRED_PEERS_ONLY=true
PREFERRED_PEERS=[
  "core-testnet1.stellar.org",
  "core-testnet2.stellar.org",
  "core-testnet3.stellar.org"
]
```
