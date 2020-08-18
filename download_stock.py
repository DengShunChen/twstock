#!/usr/bin/env python3
from stocktools import StockTools
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')
start = datetime(2020,1,1).strftime('%Y-%m-%d')
st = StockTools(start,today)
logfile = '/home/pi/twstocktiger/downloaded.txt'

def update():
  saved_stock = []
  with open(logfile,'r') as f:
    for line in f:
      saved_stock.append(line.strip())

  for sid in st.sids:
    if sid in saved_stock:
      continue
    else:
      print(sid)
      st.save_stock(sid)
      with open(logfile,'a') as f:
        f.write(sid+'\n')

for i in range(5):
  try:
    update()
  except:
    continue

st.strdate = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
st.enddate = today
st.select(force=True)
