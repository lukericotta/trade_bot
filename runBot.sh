#!/bin/bash
while :
do
  now=$EPOCHREALTIME
  git pull origin
  pip install .
  python bot/sentiment.py > "crypto.txt" 2>&1
  git add crypto.txt
  bot api_configs.yaml train_configs.yaml --export > "output.txt" 2>&1
  git pull origin
  git add output.txt
  git add sentiments.txt
  git add daily_plot.png
  git commit -m "output logs at epoch $now"
  git push origin main
done
