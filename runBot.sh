#!/bin/bash
while :
do
    git pull origin && bot api_configs.yaml train_configs.yaml
done
