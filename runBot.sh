#!/bin/bash
while :
do
    bot api_configs_crypto.yaml train_configs_crypto.yaml --crypto
    bot api_configs.yaml train_configs.yaml
done