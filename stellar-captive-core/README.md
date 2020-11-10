# Stellar Captive Core
Captive Core is a deployment that uses a stellar core node to aid horizon ingest.  If you run Horizon with Captive Stellar-Core ingestion enabled Horizon will spawn a Stellar-Core subprocess. Horizon's ingestion system will then stream ledgers from the subprocess via a filesystem pipe. The disadvantage of running both Horizon and the Stellar-Core subprocess on the same machine is it requires detailed per-process monitoring to be able to attribute potential issues (like memory leaks) to a specific service.

## Installing stellar-captive-core
Installing `stellar-captive-core` will install both `stellar-core` and `stellar-horizon` and deploy example configurations for both on the Stellar testnet.

## Configuring
Upon installation, the `stellar-captive-core` package will deploy configurations for both testnet and pubnet to `/etc/stellar/`.  By default, there will be a symlink for the testnet configuration to `/etc/stellar/stellar-core.cfg`.

### Pubnet
To configure `stellar-captive-core` for use on pubnet, create a symlink from `/etc/stellar/stellar-core_captive-pubnet.cfg` to `/etc/stellar/stellar-core.cfg` and modify `/etc/default/stellar-horizon` to update the `NETWORK_PASSPHRASE`:
```
NETWORK_PASSPHRASE="Public Global Stellar Network ; September 2015"
```
