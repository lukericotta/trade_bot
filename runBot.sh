#!/bin/bash
while :
do
    git pull origin && bot api_configs_crypto.yaml train_configs_crypto.yaml --crypto
    git pull origin && bot api_configs.yaml train_configs.yaml
done
