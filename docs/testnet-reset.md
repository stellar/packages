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

## Testnet Reset

The Testnet network is reset quarterly by the Stellar Development Foundation. The exact date will be announced with at least two weeks notice on the Stellar Dashboard as well as on several of Stellar’s online developer communities.

The reset will always occur at 09:00 UTC on the announced reset date.

Post reset you will need to perform a small maintenance in order to join/synch to the new network:

#### stellar-core maintenance overview

* stop stellar-core<br>
```# sudo systemctl stop stellar-core```
* clear/recreate `stellar` database<br>
```# sudo -u stellar psql -c 'DROP DATABASE stellar' postgres```<br>
```# sudo -u stellar psql -c 'CREATE DATABASE stellar' postgres```
* re-initialise `stellar`db schema<br>
```# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-db```
* optionally re-init your history archives (only required if you publish your own archives)<br>
```# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist ARCHIVE_NAME```
* start stellar-core<br>
```# sudo systemctl start stellar-core```

#### stellar-horizon maintenance overview

* stop stellar-horizon<br>
```# sudo systemctl stop stellar-horizon```
* clear/recreate ```horizon``` database<br>
```# sudo -u stellar psql -c 'DROP DATABASE horizon'```<br>
```# sudo -u stellar psql -c 'CREATE DATABASE horizon'```
* re-initialise ```horizon```db schema<br>
```# sudo stellar-horizon-cmd db init```
* start stellar-horizon<br>
```# sudo systemctl start stellar-horizon```
