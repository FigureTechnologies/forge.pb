# Forge.pb - Provenance Blockchain Process Manager

## Description
The Provenance Blockchain Manager is an application for automated startup of nodes on the [Provenance Blockchain](https://docs.provenance.io/) testnet, mainnet, or localnet which can be used for testing.

## Usage
In order to execute wizard, run:
```sh
forge interactive
```
* You will be prompted on what you want Forge to do. Selecting to bootstrap a node will allow you to select mainnet, testnet, or localnet.

* Selecting any of the listed 3 would clone the [Provenance Repository](https://github.com/provenance-io/provenance) if it doesn't already exist, then the version information would be gathered either from the user in the case of localnet, or from mainnet/testnet information on github. 

* The repo would then checkout to the release version and the binaries would be built, genesis file downloaded/constructed, and a command to run the node would be output to the console.


### Forge comes with command line tools that can speed up the process.

To get you started with a couple commands:

Initialize and start a localnet node with default values:
```sh
forge node start
```
For a list of all commands:
```sh
forge --help
```
You can also drill into the individual commands for more help and additional commands:
```sh
forge node --help
```

## Version Info
* Python 3.6