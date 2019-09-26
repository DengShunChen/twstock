#!/bin/bash
 
message=$1
if [ $# -eq 0 ] ; then
  message='update stockdb'
fi

cd /home/pi/twstocktiger/
rm -rf downloaded.txt
touch downloaded.txt

/usr/bin/python /home/pi/twstocktiger/download_stock.py > /home/pi/twstocktiger/logs.txt

git pull
git add stocksdb/*
git commit -am "$message"
git push heroku master

