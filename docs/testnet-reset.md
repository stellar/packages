# SDF - packages
  
1.  [Adding the SDF stable repository to your system](adding-the-sdf-stable-repository-to-your-system.md)
2.  [Quickstart](quickstart.md)
3.  [Installing individual packages](installing-individual-packages.md)
4.  [Upgrading](upgrading.md)
5.  [Bleeding Edge](bleeding-edge-unstable-repository.md)
6.  [Debug Symbols](debug-symbols.md)
7.  [Running Horizon in production](running-horizon-in-production.md)
8.  [Building Packages](building-packages.md)
9.  [Running a Full Validator](running-a-full-validator.md)
10. [Publishing a History archive](publishing-a-history-archive.md)
11. [Monitoring](monitoring.md)
12. [Testnet Reset](testnet-reset.md)

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
