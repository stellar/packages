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
echo "deb https://apt.stellar.org $(lsb_release -cs) stable" | sudo tee -a /etc/apt/sources.list.d/SDF.list
```

Please note we only support Ubuntu LTS releases.

## Adding the Bleeding Edge Testing Repository

If you would like to install our Release Candidates and/or track the Master branch, you can do so by using our `testing` repository. As the name indicates this repository and it's packages are not recommended for production deployments. Use at your own risk.

### Save the `testing` repository definition to /etc/apt/sources.list.d/SDF-testing.list:

```
echo "deb https://apt.stellar.org $(lsb_release -cs) testing" | sudo tee -a /etc/apt/sources.list.d/SDF-testing.list
```

Please note we only support Ubuntu LTS releases.
