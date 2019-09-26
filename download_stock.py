#!/usr/bin/env python
from stocktools import StockTools
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
st = StockTools(today)
logfile = '/home/pi/twstocktiger/downloaded'
print('i am in')
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
