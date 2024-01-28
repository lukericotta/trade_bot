#!/bin/bash
while :
do
  now=$EPOCHREALTIME
  mkdir "logs/$now"
  git pull origin
  pip install .
  bot api_configs.yaml train_configs.yaml --export > "logs/$now/output.txt" 2>&1
  cp sentiments.txt logs/$now/
  cp plot.png logs/$now/
  git pull origin
  git add "logs/*"
  git add sentiments.txt
  git add plot.png
  git commit -m "output logs for $now"
  git push origin main
done
