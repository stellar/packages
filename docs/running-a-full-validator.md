# SDF - packages
  
1.  [Adding the SDF stable repository to your system](adding-the-sdf-stable-repository-to-your-system.md)
2.  [Quickstart](quickstart.md)
3.  [Installing individual packages](installing-individual-packages.md)
4.  [Upgrading](upgrading.md)
5.  [Running Horizon in production](running-horizon-in-production.md)
6.  [Building Packages](building-packages.md)
7.  [Running a Full Validator](running-a-full-validator.md)
8.  [Publishing a History archive](publishing-a-history-archive.md)
9.  [Backfilling a History archive](backfilling-a-history-archive.md)
10. [Monitoring](monitoring.md)
11. [Testnet Reset](testnet-reset.md)

## Running a Full Validator
When deciding to run a Full Validator it is important to understand the requirements and benefits of doing so, it is also worth noting that to become a **Tier 1 validator operator** one must run at least 3 full validators in geographically distinct zones and have a demonstrable [high validator uptime](https://www.stellarbeat.io/nodes).

### Benefits
Running a full validator is not only beneficial to the operator but is also a great way to contribute to the general health of the Stellar network. Full validators are the true measure of how decentralized and redundant the network is as they are the only type of validators that perform all functions on the network. Listed below are some of the operator level benefits.

* Enables deeper integrations by clients and business partners
* Official endorsement of specific ledgers in real time (via signatures)
* Quorum Set aligned with business priorities
* Additional checks/invariants enabled
  * Validator can halt and/or signal that for example (in the case of an issuer) that it does not agree to something

### Requirements
Running a full validator is a fairly straightforward process and depending on your capacity requirements needs very little computing resources.

* server/instance to run the stellar-core application and corresponding postgres database
* secrets management to securely store the seed(s)
* access to an Object store such as S3/Spaces/Azure Blob for storing history (optional, can also be stored and served locally)
* monitoring (optional, can also be plugged into existing monitoring)

For more in-depth requirements please see the main [admin guide](https://developers.stellar.org/docs/run-core-node).

#### Required Steps

1. install stellar-core
2. configure validation
3. publish history

### Installing stellar-core
For this guide we will be documenting the process of installing the `stellar-core-postgres` Debian package. As described in more detail [here](quickstart.md#moving-on-from-quickstart), the `stellar-core-postgres` package pulls in the `stellar-core` package and configures a local PostgreSQL database server ready for use by stellar-core, please note that by default this package connects `stellar-core` to the **Testnet** as a simple watcher node.

Install stellar-core and a local postgres database using PostgreSQL's `peer authentication method` for authentication/security:

* `apt-get install stellar-core-postgres`

Accessing the locally configured `stellar` PostgreSQL database and running stellar-core commands such as `new-db` is described in more detail [here](quickstart.md#accessing-the-quickstart-databases).

Alternatively if you prefer to install and configure PostgreSQL yourself, you will only need to install the `stellar-core` package.

* `apt-get install stellar-core`

### Configuration

Once you have configured your stellar-core node and it's respective database, you will need to configure your stellar-core instance to become a **Full Validator**. The simplest way to create a validator configuration is to start off with a working `watcher` config and simply add the required validator configuration parameters (`NODE_IS_VALIDATOR`, `NODE_SEED`).

As mentioned previously, the configuration installed by the `stellar-core-postgres` package configures `stellar-core` to connect to the SDF **Testnet** as a basic watcher node. Connecting to the **Pubnet** as a watcher is simply a matter of modifying the `stellar-core` configuration to point to **Pubnet** and running `sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-db` to reset the database and buckets directory.

If you want to create a **Pubnet** validator, you can use the [**Pubnet Watcher**](stellar-core_pubnet_watcher.cfg) config.

#### Validation
Configuring a node to participate in SCP and sign messages is a 3 step process consisting of securely generating a `seed`, adding this seed to your configuration file and finally setting the `NODE_IS_VALIDATOR=true` parameter.

* create a keypair `stellar-core gen-seed`
* add `NODE_SEED="SD7DN..."` to your configuration file
* add `NODE_IS_VALIDATOR=true` to your configuration file

You will most likely want to share the public portion of your keypair to other validator operators so that they can add your nodes to their quorum set. This is best achieved by publishing a [.well-known/stellar.toml](https://www.stellar.org/.well-known/stellar.toml) on your homedomain, you can also use it to share other aspects of your nodes configuration, such as history archive location, organisation name, etc.

Storing your node seed securely is essential, if someone else has access to it they can send messages to the network and these will appear to originate from your node.

#### Quorum Set
The quorum set is used by stellar-core to define which nodes on the network you trust as well as to configure stellar-core's behaviour during arbitrary node failures. More information can be found in the [quorum set](https://www.stellar.org/developers/stellar-core/software/admin.html#crafting-a-quorum-set) section of the main admin guide.

### Publishing History
Full validators participate in consensus and publish their history data either to a blob store such S3, Spaces or Azure Blob. This aspect of the full validator is incredibly important as it enables other network users to connect and sync to the network using your validator thus increasing network resiliency and decentralisation.

The process of publishing `stellar-core` history is described in detail [here](publishing-a-history-archive.md)
