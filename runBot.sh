#!/bin/bash
while :
do
  now=$EPOCHREALTIME
  git pull origin
  pip install .
  bot api_configs.yaml train_configs.yaml --export > "output.txt" 2>&1
  python bot/plotAlpaca.py
  git pull origin
  git add output.txt
  git add sentiments.txt
  git add plot.png
  git commit -m "output logs at epoch $now"
  git push origin main
done
