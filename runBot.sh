#!/bin/bash
while :
do
    git pull origin && pip install -e . && bot api_configs.yaml train_configs.yaml
done
