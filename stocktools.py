#!/usr/bin/env python
import twstock
from twstock import stock
from twstock import realtime
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import json

class StockTools(object):

  class StockReal(object):

    def __init__(self,sid:str):
        self.sid = sid
        
    def get_data(self):
        self.real_data = realtime.get(self.sid)
        self.real = self.real_data['realtime']
        self.info = self.real_data['info']
        self.latest_trade_price = self.real['latest_trade_price']
        self.accumulate_trade_volume = self.real['accumulate_trade_volume']
        self.best_bid_price = self.real['best_bid_price']
        self.best_ask_price = self.real['best_ask_price']
        self.best_bid_volume = self.real['best_bid_volume']
        self.best_ask_volume = self.real['best_ask_volume']
        self.start = self.real['open']
        self.high = self.real['high']
        self.low = self.real['low']

    def plot(self):
        fig, ax1 = plt.subplots(figsize=(10, 3))
        x1 = [1,1,1,1,1]
        x3 = [1]

        bb = [ float(price) for price in self.best_bid_price ]
        ba= [ float(price) for price in self.best_ask_price ]
        bbv = [ float(price) for price in self.best_bid_volume ]
        bav= [ float(price) for price in self.best_ask_volume ]
        
        yh = [float(self.high)] 
        yl = [float(self.low)]
        op = [float(self.start)]
        price = [float(self.latest_trade_price)]

        ax1.plot(ba,x1,color='r',marker='.',label='賣出價格')
        ax1.plot(bb,x1,color='b',marker='.',label='買進價格')

        ax1.scatter(yh,x3,s=50,color='r',marker='X',label='最高價'+self.high)
        ax1.scatter(yl,x3,s=50,color='b',marker='X',label='最低價'+self.low)
        
        ax1.scatter(op,[2],s=50,color='k',marker='h',label='開盤價'+self.start)
        diff = price[0] - op[0]
        if diff > 0:
            color = 'r'
            marker= '^'
        else:
            color = 'g'
            marker='v'
        ax1.scatter(price,[2],s=50,color=color,marker=marker,label='現價'+self.latest_trade_price)
        
        ax1.set_ylim(0,4)
        ax1.set_yticklabels([])
        
        ax1.set_title(self.info['fullname']+'  '+self.info['time'])
        
        ax2 = ax1.twinx()
        ax2.plot(ba,bav,color='r',label='賣出數量',linestyle='dashed',alpha=0.5)
        ax2.plot(bb,bbv,color='b',label='買進數量',linestyle='dashed',alpha=0.5)        
        ax2.set_ylim(0,1500)
        
        ax1.legend(loc='upper right')
        ax2.legend(loc='upper left')
                 
        plt.tight_layout()
        plt.savefig(self.sid+'.pdf')
        plt.savefig(self.sid+'.png')
        plt.show()

  def __init__(self,strdate=None,enddate=None):

    self.firstdate = 'None'
    self.lastdate = 'None'

    self.strdate = strdate
    self.enddate = enddate

    self.threshold = 0.002
    #self.ma20_factor = 0.01        # 10% make sure the price just over/below ma20
    self.ma20_factor = 0.02        # 10% make sure the price just over/below ma20
    self.capacity_bound = 2000
    self.bigcapa_factor = 1.5

    self.sids = []
    self.twse = twstock.twse
    for sid in self.twse.keys():
      if self.twse[sid].type == '股票':
        self.sids.append(sid)

    #register matplotlib converters
    register_matplotlib_converters()
    self.dbdir='stocksdb'

  def save_stock(self,sid:str):
    self.stock_data = stock.Stock(sid)

    if self.strdate == None and self.enddate == None:
      self.strdate = datetime.now().strftime("%Y-%m-%d")
    elif self.enddate == None:
      year = int(self.strdate[0:4]) ; month = int(self.strdate[5:7])
      self.stock_data.fetch(year=year,month=month)
    else:
      syear = int(self.strdate[0:4]) ; smonth = int(self.strdate[5:7])
      eyear = int(self.enddate[0:4]) ; emonth = int(self.enddate[5:7])
      self.stock_data.fetch_from_to(syear=syear,smonth=smonth,eyear=eyear,emonth=emonth)

    try:
      os.mkdir(self.dbdir)
    except:
      pass

    dbname = '%s/%s.db' % (self.dbdir,sid)

    conn = sqlite3.connect(dbname,detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS stocks
        (date timestamp, capacity integer, turnover text, open real, high real, 
        low real, close real, change real, transactions integer)''')

    # Creat unique index
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS date_unique ON stocks (date)')

    # Insert a row of data
    for data in self.stock_data.data:
      cursor.execute("INSERT OR IGNORE INTO stocks VALUES (?,?,?,?,?,?,?,?,?)",data)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

  def read_stock(self,sid:str):
    if self.enddate == None:
      self.enddate = datetime.now().strftime("%Y-%m-%d")

    dbdir = 'stocksdb'
    dbname = '%s/%s.db' % (dbdir,sid)
    conn = sqlite3.connect(dbname,detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Read table
    sqlite_data = cursor.execute('''SELECT * FROM stocks WHERE date >= datetime(?) AND date <= datetime(?)''',(self.strdate,self.enddate))
    self.stock_pd = pd.DataFrame(sqlite_data,columns=['date', 'capacity', 'turnover', 'open', 'high', 'low', 'close', 'change', 'transaction'])
    
    self.firstdate = self.stock_pd.date.iloc[0].strftime('%Y%m%d')
    self.lastdate = self.stock_pd.date.iloc[-1].strftime('%Y%m%d')

    return self.stock_pd

  def get_stockids(self):
    sids = []
    twse = twstock.twse
    for sid in twse.keys():
        if twse[sid].type == '股票':
            sids.append(sid)
    return sids

  def fetch_all(self):
    for sid in self.sids:
      print('Downloading ...%5s'%(sid))
      try:
        self.save_stock(sid)
      except:
        print(self.twse[sid].name,sid,' Calculate failed')

  def _stock_anal(self,sid:str,real:bool=False):
    # read in data 
    self.read_stock(sid)

    if real:
      data = realtime.get(sid)
      real_data = data['realtime']
      real_info = data['info']
      latest_trade_price = real_data['latest_trade_price']
      accumulate_trade_volume = real_data['accumulate_trade_volume']
      datalist = [[datetime.now(),int(accumulate_trade_volume)*1000,None,None,None,None,latest_trade_price,None,None],]
      labelist = ['date','capacity','turnover','open','high','low','close','change','transaction']
      real_pd = pd.DataFrame(datalist, columns=labelist)
      self.stock_pd = self.stock_pd.append(real_pd, ignore_index=True)
      timestamp = real_info['time']
    else:
      timestamp = ''
      
    self.stock_pd = self.stock_pd.set_index('date')
    if self.stock_pd.shape[0] == 0:
      raise DataEmptyError

    ma03 = self.stock_pd.rolling(3).mean()
    ma05 = self.stock_pd.rolling(5).mean()
    ma08 = self.stock_pd.rolling(8).mean()
    ma20 = self.stock_pd.rolling(20).mean()
    ma60 = self.stock_pd.rolling(60).mean()
   
    self.ma_pd = pd.concat([ma03['close'],ma05['close'],ma08['close'],ma20['close'],ma60['close']],axis=1)
    self.ma_pd.columns=['ma03','ma05','ma08','ma20','ma60']
    self.ma_std  = self.ma_pd.loc[:,['ma03','ma05','ma08']].std(axis=1) 
    self.ma_mean = self.ma_pd.loc[:,['ma03','ma05','ma08']].mean(axis=1)
    self.norstd = self.ma_std.div(self.ma_mean)
    self.name = self.twse[sid].name
    self.id = int(sid)
    self.timestamp = timestamp 
    self.stock_pd[['capacity']] = self.stock_pd[['capacity']] /1000

    #data['slop'] = 0.5*(stock_pd['close'].iloc[-1] - stock_pd['close'].iloc[-3])
    #data['slop'] = 0.5*(stock_ma03['close'].iloc[-1] - stock_ma03['close'].iloc[-2])
    #data['slop'] = 0.5*(stock_ma03['close'].iloc[-1] - stock_ma03['close'].iloc[-3])
    self.slop = 0.5*(self.ma_pd.ma05.iloc[-1] - self.ma_pd.ma05.iloc[-2])
    self.nstdslop = 0.5*(self.norstd.iloc[-1] - self.norstd.iloc[-2])

  def plot(self,sid:str,real=False,buyprice:float=None):

    self._stock_anal(sid,real)

    def make_patch_spines_invisible(ax):
      ax.set_frame_on(True)
      ax.patch.set_visible(False)
      for sp in ax.spines.values():
        sp.set_visible(False)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    fig.subplots_adjust(right=0.8)

    ax1.set_xlabel('日期')
    ax1.set_ylabel('價格（每股）')

    ax1.plot(self.ma_pd.ma03, '-' , label="3日均價",zorder=10, linewidth=2)
    ax1.plot(self.ma_pd.ma05, '-' , label="5日均價",zorder=10, linewidth=2)
    ax1.plot(self.ma_pd.ma08, '-' , label="8日均價",zorder=10, linewidth=2)
    ax1.plot(self.ma_pd.ma20, '-' , label="20日均價",zorder=10, linewidth=2)
    ax1.plot(self.ma_pd.ma60, '-' , label="60日均價",zorder=10, linewidth=2)
    ax1.plot(self.stock_pd.close, '-' , label="收盤價",color='k',zorder=10, linewidth=2.4)
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.legend(loc='best')
    if buyprice != None:
      ax1.axhline(y=buyprice, color='k', alpha=0.5, zorder=6)
    plt.grid(True,which='both')

    ax2 = ax1.twinx()
    ax2.spines["right"].set_position(("axes", 1.1))
    make_patch_spines_invisible(ax2)
    ax2.spines["right"].set_visible(True)
    ax2.set_ylabel('變異係數',color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.plot(self.norstd, label="3,5,8日離散度",color='b',alpha=0.5, zorder=5)
    ax2.axhline(y=self.threshold, color='r', alpha=0.5, zorder=6)
    #ax2.legend(loc='upper right')

    ax3 = ax1.twinx()
    ax3.set_ylabel('成交量(張)',color='g')
    ax3.tick_params(axis='y', labelcolor='g')
    ax3.bar(self.stock_pd.index,self.stock_pd.capacity, width=1.2,label="成交量",color='g',alpha=0.3, zorder=0)
    #ax3.legend(loc='upper center')

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.title('%s %d %s 股市分析圖   ' % (self.timestamp,self.id,self.name) ,loc='right')
    plt.tight_layout()

    fig.savefig('analysis_%d%s.png' % (self.id,self.name))
    fig.savefig('analysis_%d%s.pdf' % (self.id,self.name))

    plt.show()

  def select(self,force=False):

    with open('seleted_stocks.json', 'r') as f:
      selected_json = json.load(f)
   
    if self.enddate not in selected_json.keys() or force: 
      buy='' ; sell=''
      selected_sids = {} ; selected_sids['buy'] = [] ; selected_sids['sell'] = []
      for sid in self.sids:
        # 讀取資料
        try:
          self._stock_anal(sid)
        except:
          continue
          #print('%-8s %-4s Calculate failed'%(twse[sid].name,sid))
 
        # 必要篩選條件
        bound = self.stock_pd.capacity.iloc[-1] > self.capacity_bound
        if self.norstd[-1] < self.threshold and bound and self.nstdslop > 0 :
          # 爆大量分析
          capacond = self.stock_pd.capacity.iloc[-1] > self.bigcapa_factor * self.stock_pd.capacity.iloc[-2]
          if capacond:
            capamark='爆大量'
          else:
            capamark=''
 
          # 股票基本資訊
          stockinfo = '%4.4s %6.5f %6.2f %7.2f %6d %-8.8s %3s'% (sid,self.norstd[-1],self.stock_pd.close.iloc[-1], \
                  self.ma_pd.ma20.iloc[-1],self.stock_pd.capacity.iloc[-1],self.twse[sid].name,capamark)
          # 股票篩選機制
          ma20diff = self.stock_pd.close.iloc[-1] - self.ma_pd.ma20.iloc[-1]
          if   ma20diff > 0 and ma20diff <  self.ma20_factor * self.ma_pd.ma20[-1] and self.slop > 0:
            buy  =  buy + ' BUY: ' + stockinfo + '\n'
            selected_sids['buy'].append(sid)
          elif ma20diff < 0 and ma20diff > -self.ma20_factor * self.ma_pd.ma20[-1] and self.slop < 0:
            sell = sell + 'SELL: ' + stockinfo + '\n'
            selected_sids['sell'].append(sid)
      print('有效日期：',self.lastdate)
      print('%3s %3s%6s%6s%6s%5s%3s'%('買賣','股號','離散度','股價','20日均價','成交量','股名'))
      print(buy + sell)

      selected_json[self.enddate] = selected_sids
      with open('seleted_stocks.json', 'w') as f:
        json.dump(selected_json, f)
    else:
      selected_sids = selected_json[self.enddate]
    
    print(selected_sids)
    return selected_sids

if __name__ == '__main__':
  st = StockTools('2019-01-01','2019-02-01')
  st.select()
