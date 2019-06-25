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

