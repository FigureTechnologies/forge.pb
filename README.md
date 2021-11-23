# Forge.pb - Provenance Blockchain Process Manager

## Description
The Provenance Blockchain Manager is an application for automated startup of nodes on the [Provenance Blockchain](https://docs.provenance.io/) testnet, mainnet, or localnet which can be used for testing.

## Usage
In order to execute, run:
```sh
forge
```
* You will be prompted on what you want PBPM to do. Selecting to bootstrap a node will allow you to select mainnet, testnet, or localnet.

* Selecting any of the listed 3 would clone the [Provenance Repository](https://github.com/provenance-io/provenance) if it doesn't already exist, then the version information would be gathered either from the user in the case of localnet, or from mainnet/testnet information on github. 

* The repo would then checkout to the release version and the binaries would be built, genesis file downloaded/constructed, and a command to run the node would be output to the console.

## Version Info
* Python 3.6