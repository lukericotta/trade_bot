# BoptimalTrader #

This package provides a python library with commonly used classes and functions.

## Capabilities ##

**Python Application Programming Interface (API)**

* BoptimalTrader

## Future Capabilities ##

* Unit tests

## Installation ##

### For All Users ###

To install the python toolbox, it is recommended to first install conda dependencies with the following command.

```bash
conda create -y -n trading_env python=3.8
conda activate trading_env
conda env update --file requirements.yaml
```

To install required python packages required by the bot.

```bash
pip install alpaca-py
pip install alpaca-trade-api
```

### For Users

Execute the following command to install the toolbox:

```bash
pip install .
```

Execute the following command to install en editable version of the toolbox:

```bash
pip install -e .
```

## Usage

### Python API with stock trading (S&P 500)
```bash
bot api_configs.yaml trading/train_configs.yaml
```

### Python API with crypto trading (see train_config.yaml)
```bash
bot api_configs.yaml trading/train_configs.yaml --crypto
```
