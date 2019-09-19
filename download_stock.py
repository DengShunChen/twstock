#!/usr/bin/env python
from stocktools import StockTools
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
st = StockTools(today)

saved_stock = []
with open('downloaded','r') as f:
  for line in f:
    saved_stock.append(line.strip())

f = open('downloaded','a')
for sid in st.sids:
  print(sid)
  if sid in saved_stock:
    continue
  else:
    st.save_stock(sid)
    f.write(sid+'\n')

f.close()
