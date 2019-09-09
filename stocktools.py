#!/usr/bin/env python
import twstock
from twstock import stock
from twstock import realtime
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys
import matplotlib.pyplot as plt

class StockTools(object):
  def __init__(self):
    self.sids = []
    self.twse = twstock.twse
    for sid in self.twse.keys():
      if self.twse[sid].type == '股票':
        self.sids.append(sid)

  def save_stock(self,sid:str,strdate=None):
    stock_data = stock.Stock(sid)

    if strdate == None:
      strdate = datetime.now().strftime("%Y%m%d")
    else:
      year = int(strdate[0:4]) ; month = int(strdate[4:6])
      stock_data.fetch(year=year,month=month)

    try:
      os.mkdir(strdate)
    except:
      pass

    conn = sqlite3.connect('%s/%s.db' % (strdate,sid),detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS stocks
        (date timestamp, capacity integer, turnover text, open real, high real, 
        low real, close real, change real, transactions integer)''')

    # Insert a row of data
    for data in stock_data.data:
      cursor.execute("INSERT INTO stocks VALUES (?,?,?,?,?,?,?,?,?)",data)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

  def read_stock(self,sid:str,strdate=None):
    if strdate == None:
      strdate = datetime.now().strftime("%Y%m%d")

    conn = sqlite3.connect('%s/%s.db' % (strdate,sid),detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Read table
    sqlite_data = cursor.execute('SELECT * FROM stocks').fetchall()

    data_pd = pd.DataFrame(sqlite_data,columns=['date', 'capacity', 'turnover', 'open', 'high', 'low', 'close', 'change', 'transaction'])

    return data_pd

  def get_stockids(self):
    sids = []
    twse = twstock.twse
    for sid in twse.keys():
        if twse[sid].type == '股票':
            sids.append(sid)
    return sids

  def fetch_stock_all(self,strdate=None):
    for sid in self.sids:
      print('Downloading ...%5s'%(sid))
      try:
        self.read_stock(sid,strdate)
      except:
        try:
          self.save_stock(sid,strdate)
        except:
          print(self.twse[sid].name,sid,' Calculate failed')

  def _stock_anal(self,sid:str,strdate=None,sqldb=True):
    if sqldb:
      stock_pd = self.read_stock(sid,strdate)
    else:
      stock_data = stock.Stock(sid).fetch_days(180)
      stock_pd = pd.DataFrame(stock_data)

    stock_pd = stock_pd.set_index('date')
    stock_ma3 = stock_pd.rolling(3).mean()
    stock_ma5 = stock_pd.rolling(5).mean()
    stock_ma8 = stock_pd.rolling(8).mean()
    data = pd.concat([stock_ma3['close'],stock_ma5['close'],stock_ma8['close']],axis=1)
    std = data.std(axis=1) ; mean = data.mean(axis=1)

    data = {}
    data['stock_pd'] = stock_pd
    data['stock_ma3'] = stock_ma3
    data['stock_ma5'] = stock_ma5
    data['stock_ma8'] = stock_ma8
    data['stock_ma20'] = stock_pd.rolling(20).mean()
    data['stock_ma60'] = stock_pd.rolling(60).mean()
    data['stock_std'] = std
    data['stock_norstd'] = std.div(mean)
    data['stock_name'] = self.twse[sid].name
    data['stock_id'] = int(sid)

    return data

  def plot(self,sid:str,strdate=None,sqldb=True):

    data = self._stock_anal(sid,strdate=strdate,sqldb=sqldb)

    def make_patch_spines_invisible(ax):
      ax.set_frame_on(True)
      ax.patch.set_visible(False)
      for sp in ax.spines.values():
        sp.set_visible(False)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    fig.subplots_adjust(right=0.8)

    ax1.set_xlabel('日期')
    ax1.set_ylabel('價格（每股）')

    ax1.plot(data['stock_pd'].close, '-' , label="收盤價",color='k',zorder=10)
    ax1.plot(data['stock_ma3'].close, '-' , label="3日均價",zorder=10)
    ax1.plot(data['stock_ma5'].close, '-' , label="5日均價",zorder=10)
    ax1.plot(data['stock_ma8'].close, '-' , label="8日均價",zorder=10)
    ax1.plot(data['stock_ma20'].close, '-' , label="20日均價",zorder=10)
    ax1.plot(data['stock_ma60'].close, '-' , label="60日均價",zorder=10)
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.legend(loc='best')

    ax2 = ax1.twinx()

    ax2.spines["right"].set_position(("axes", 1.1))
    make_patch_spines_invisible(ax2)
    ax2.spines["right"].set_visible(True)

    ax2.set_ylabel('變異係數',color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.plot(data['stock_norstd'], label="3,5,8日離散度",color='b',alpha=0.5, zorder=20)
    #ax2.legend(loc='upper right')

    ax3 = ax1.twinx()
    ax3.set_ylabel('成交量(張)',color='g')
    ax3.tick_params(axis='y', labelcolor='g')
    ax3.bar(data['stock_pd'].index,data['stock_pd'].capacity.div(1000), width=1.2,label="成交量",color='g',alpha=0.3, zorder=0)
    #ax3.legend(loc='upper center')

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.title('%d %s 股市分析圖   ' % (data['stock_id'],data['stock_name']) ,loc='right')
    plt.grid(True,which='both')
    plt.tight_layout()

    fig.savefig('analysis_%d%s.png' % (data['stock_id'],data['stock_name']))
    fig.savefig('analysis_%d%s.pdf' % (data['stock_id'],data['stock_name']))
    plt.show()

  def _get_info(self,sid:str,strdate=None):
    stock_pd = self.read_stock(sid,strdate)
    stock_pd = stock_pd.set_index('date')
    if stock_pd.shape[0] == 0:
      raise DataEmptyError

    stock_ma3 = stock_pd.rolling(3).mean()
    stock_ma5 = stock_pd.rolling(5).mean()
    stock_ma8 = stock_pd.rolling(8).mean()
    stock_ma20 = stock_pd.rolling(20).mean()

    data = pd.concat([stock_ma3['close'],stock_ma5['close'],stock_ma8['close']],axis=1)
    std = data.std(axis=1)
    mean = data.mean(axis=1)

    close = stock_pd[['close']]
    capacity = stock_pd[['capacity']] /1000

    data = {}
    data['norstd'] = std / mean
    data['close'] = close
    data['capacity'] = capacity
    data['ma20'] = stock_ma20['close']
    data['slop'] = 0.5*(stock_pd['close'].iloc[-1] - stock_pd['close'].iloc[-3])

    return data

  def select(self,strdate=None):
    threshold = 0.002
    ma20_factor = 0.01        # 10% make sure the price just over/below ma20
    capacity_bound = 2000
    bigcapa_factor = 1.5

    buy=''
    sell=''
    for sid in self.sids:
      # 讀取資料
      try:
        data = self._get_info(sid,strdate)
      except:
        continue
        #print('%-8s %-4s Calculate failed'%(twse[sid].name,sid))

      # 必要篩選條件
      bound = data['capacity'].iloc[-1] > capacity_bound
      if data['norstd'][-1] < threshold and bound['capacity']:
        # 爆大量分析
        capacond = data['capacity'].iloc[-1] > bigcapa_factor * data['capacity'].iloc[-2]
        if capacond['capacity']:
          capamark='爆大量'
        else:
          capamark=''

        # 股票基本資訊
        stockinfo = '%4.4s %6.5f %6.2f %7.2f %6d %-8.8s %3s'% (sid,data['norstd'][-1],data['close'].iloc[-1], \
                data['ma20'].iloc[-1],data['capacity'].iloc[-1],self.twse[sid].name,capamark)
        # 股票篩選機制
        ma20diff = data['close'].iloc[-1] - data['ma20'].iloc[-1]
        if ma20diff['close'] > 0 and ma20diff['close'] < ma20_factor*data['ma20'][-1] and data['slop'] > 0:
          buy  =  buy + ' BUY: ' + stockinfo + '\n'
        elif ma20diff['close'] < 0 and ma20diff['close'] > -ma20_factor*data['ma20'][-1] and data['slop'] < 0:
          sell = sell + 'SELL: ' + stockinfo + '\n'
    print('%3s %3s%6s%6s%6s%5s%3s'%('買賣','股號','離散度','股價','20日均價','成交量','股名'))
    print(buy)
    print(sell)

if __name__ == '__main__':
  st = StockTools()
  #print(st.get_stock('2330'))
  #print(st._get_info('2330'))
  #st.plot(st.stock_anal('1101','20180801'))
  #st.plot(st.stock_anal('1101'))
  st.select() 
