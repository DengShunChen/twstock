#!/bin/bash
set -x
 
message=$1
if [ $# -eq 0 ] ; then
  message='daily update stockdb'
fi

cd /home/pi/twstocktiger/
rm -rf downloaded.txt
touch downloaded.txt

python3 download_stock.py

git pull
git add stocksdb/*
git add seleted_stocks.json
git commit -am "$message"
git push heroku master

