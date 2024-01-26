#!/bin/bash
while :
do
	now=$EPOCHREALTIME
	git pull origin && pip install -e . && bot api_configs.yaml train_configs.yaml > "output-$now.txt" 2>&1
	git pull origin
	git add "output-$now.txt"
	git commit -m "output log for $now"
	git push origin main
done
