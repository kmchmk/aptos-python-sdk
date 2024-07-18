# THB Stable Coin

This provides basic functionalities to mint xxTHB stable coin on Aptos blockchain.

## Setup
This SDK uses [Poetry](https://python-poetry.org/docs/#installation) for packaging and dependency management:

```
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry self add poetry-plugin-dotenv
```

Create a .env file on the root folder and add the following variables.

```
MY_LOCAL_ACCOUNT_PRIVATE_KEY=
MY_WEB_ACCOUNT_ADDRESS=
```

## Compile, Upload, Mint and Transfer
Execute the following [execute.sh](./execute.sh) file.

```bash
./execute.sh
```

## Note
To get a better understanding of the repo, please refer to the parent repo's [README.md](https://github.com/aptos-labs/aptos-python-sdk/blob/main/README.md).