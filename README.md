# Forge.pb - Provenance Blockchain Process Manager

## Description
The Provenance Blockchain Manager is an application for automated startup of nodes on the [Provenance Blockchain](https://docs.provenance.io/) testnet, mainnet, or localnet which can be used for testing.

## Getting Started
Forge is available on [Pypi](https://pypi.org/project/forge.pb/) and the repo is on [GitHub](https://github.com/provenance-io/forge.pb) and can be installed using pip.
```
pip install forge.pb
```
or
```
pip install forge.pb==1.0.1
```
if you want to install a specific version

## Usage
Once installed, you can execute wizard, by running: 
```sh
forge interactive
```
* You will be prompted on what you want Forge to do. Selecting to bootstrap a node will allow you to select mainnet, testnet, or localnet.

* Selecting any of the listed 3 would clone the [Provenance Repository](https://github.com/provenance-io/provenance) if it doesn't already exist, then the version information would be gathered either from the user in the case of localnet, or from mainnet/testnet information on github. 

* The repo would then checkout to the release version and the binaries would be built, genesis file downloaded/constructed, and a command to run the node would be output to the console.

### Optional

Forge uses the GitHub Api to pull information about the provenance repo for you to use when spinning up a node. If you use forge a lot in a short time, you could hit the 60 calls per hour limit. You can add a GitHub Api Token to your environment in order to increase this to 5000 calls per hour.

You can follow the instructions [Here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to setup a personal access token.
Once that is complete, add the token generated to your environment:
```sh
GITHUB_API_TOKEN=token_value
```

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