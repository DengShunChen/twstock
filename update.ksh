#!/bin/bash
 
message=$1
if [ $# -eq 0 ] ; then
  message='daily update stockdb'
fi

cd /home/pi/twstocktiger/
rm -rf downloaded.txt
touch downloaded.txt

/usr/bin/python /home/pi/twstocktiger/download_stock.py > /home/pi/twstocktiger/logs.txt

git pull
git add stocksdb/*
git add seleted_stocks.json
git commit -am "$message"
git push heroku master

