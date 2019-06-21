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
| stellar-core-utils                | none                        | installs useful command line tools (stellar-core-cmd, stellar-core-gap-detect)     |
| stellar-core-prometheus-exporter  | none                        | installs a Prometheus exporter to facilitate ingesting stellar-core metrics        |
| stellar-core-postgres             | stellar-core, PostgreSQL    | configures a PostgreSQL server, creates a stellar db,role and system user          |
| stellar-archivist                 | none                        | installs stellar-archivist cli tool for managing stellar-core History archives     |
| stellar-horizon                   | none                        | installs stellar-horizon binary, systemd service                                   |
| stellar-horizon-utils             | none                        | installs useful command line tools (stellar-horizon-cmd)                           |
| stellar-horizon-postgres          | stellar-horizon, PostgreSQL | configures a PostgreSQL server, creates a horizon db and stellar role, system user |
| stellar-quickstart                | stellar-core-postgres, stellar-horizon-postgres | pulls in required packages via it's dependencies               |

Once you are comfortable with the various packages that `stellar-quickstart` brings in as dependencies, it is possible to install them individually.

See [Running Horizon in production](#running-horizon-in-production) for a generic distributed Horizon cluster, you will need to configure **PostgreSQL** which unfortunately is out of the scope of this document.
