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

## Bleeding Edge Unstable Repository

If you would like to install our Release Candidates and/or track the Master branch, you can do so by using our `unstable` repository. As the name indicates this repository and it's packages are not recommended for production deployments. Use at your own risk.

### Save the `unstable` repository definition to /etc/apt/sources.list.d/SDF-unstable.list:

```
echo "deb https://apt.stellar.org/public unstable/" | sudo tee -a /etc/apt/sources.list.d/SDF-unstable.list
```
