#!/bin/ksh
 
message=$1
if [ $# -eq 0 ] ; then
  message='make it better'
fi

git add .
git commit -am "$message"
git push heroku master
heroku logs --tail
