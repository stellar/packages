# Stellar Captive Core API
The Captive Stellar-Core Server allows you to run a dedicated Stellar-Core instance for the purpose of ingestion. The server must be bundled with a Stellar Core binary.

If you run Horizon with Captive Stellar-Core ingestion enabled Horizon will spawn a Stellar-Core subprocess. Horizon's ingestion system will then stream ledgers from the subprocess via a filesystem pipe. The disadvantage of running both Horizon and the Stellar-Core subprocess on the same machine is it requires detailed per-process monitoring to be able to attribute potential issues (like memory leaks) to a specific service.

Now you can run Horizon and pair it with a remote Captive Stellar-Core instance. The Captive Stellar-Core Server can run on a separate machine from Horizon. The server will manage Stellar-Core as a subprocess and provide an HTTP API which Horizon can use remotely to stream ledgers for the purpose of ingestion.

Note that, currently, a single Captive Stellar-Core Server cannot be shared by multiple Horizon instances.

## More Info
More information and the API specifications can be found at: https://github.com/stellar/go/tree/master/exp/services/captivecore
