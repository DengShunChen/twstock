#!/usr/bin/env python 
from stocktools import StockTools
import dash
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html

import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
import time

#app = dash.Dash(
#    __name__, 
#    assets_external_scripts='https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
#)

# dash 
app = dash.Dash(__name__)
server = app.server

app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions=True
app.title = 'Tiger'    

colorscale2 = cl.scales['12']['qual']['Paired']
colorscale1 = cl.scales['11']['div']['RdYlGn']

logoimgsrc = "https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png"
logoimgsrc = "https://www.sccpre.cat/mypng/full/69-695057_background-images-hd-picsart-png-tiger-logo-clip.png"
logoimgsrc = "https://st2.depositphotos.com/5486388/8173/v/950/depositphotos_81739398-stock-illustration-tiger-logo-template.jpg"
workingimg = "http://nas.cyes.ntpc.edu.tw/wordpress/periodical/wp-content/uploads/sites/25/2017/12/construction-300x149.png"

benner = [
      html.H1('台灣股虎',
      style={'display': 'inline',
         'float': 'center',
         'font-size': '2.0em',
         'margin-left': '0px',
         'font-weight': 'bolder',
         'font-family': 'Product Sans',
         'color': "rgba(178, 223, 138, 0.95)",
         'margin-top': '0px',
         'margin-bottom': '10px'
         }),
      html.Img(src=logoimgsrc,
        style={'display': 'inline',
          'height': '100px',
          'float': 'right'
        }
      ),
      html.P(),
]

TAB_STYLE = {
    'width': 'inherit',
    'border': 'none',
    'boxShadow': 'inset 0px -1px 0px 0px lightgrey',
    'background': 'white',
    'paddingTop': 0,
    'paddingBottom': 0,
    'height': '42px',
}

SELECTED_STYLE = {
    'width': 'inherit',
    'boxShadow': 'none',
    'borderLeft': 'none',
    'borderRight': 'none',
    'borderTop': 'none',
    'borderBottom': '2px #004A96 solid',
    'background': 'lightblue',
    'paddingTop': 0,
    'paddingBottom': 0,
    'height': '42px',
}

app.layout = html.Div([
    html.Div(benner),
    html.Div(id='tabs-content-classes'),
    dcc.Tabs(
        id="tabs-with-classes",
        value='tab-1',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='選股',
                value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=TAB_STYLE,
                selected_style=SELECTED_STYLE,
                children=[
                  html.Div([
                    html.Div('資料日期：',style={'display': 'inline'}),
                    html.Div([
                      dcc.DatePickerRange(
                        id='date-picker-range1',
                        min_date_allowed=dt.datetime(2000, 1, 1),
                        max_date_allowed=dt.datetime(2100, 12, 31),
                        initial_visible_month=dt.datetime.now(),
                        display_format='M-D-Y',
                        end_date=dt.datetime.now(),
                        start_date=dt.datetime.now() - dt.timedelta(days=180) 
                      ),
                    ],style={'display': 'inline'}),
                    html.Div('  選股日期:',style={'display': 'inline'}),
                    html.Div([
                      dcc.DatePickerSingle(
                        id='date-picker-single1',
                        min_date_allowed=dt.datetime(2000, 1, 1),
                        max_date_allowed=dt.datetime(2100, 12, 31),
                        initial_visible_month=dt.datetime.now(),
                        display_format='M-D-Y',
                        date=dt.datetime.now(),
                      )
                    ],style={'display': 'inline'}),
                    html.Div('  更新:',style={'display': 'inline'}),
                    daq.PowerButton(
                      id='power-button1',
                      on=False,
                      color='#FF5E5E',
                      size=45,
                      style={'display':'inline','float': 'right','margin-right': '350px'},
                    ),
                  ]),
                  dcc.Dropdown(
                    id='stock-ticker-input',
                    multi=True
                  ),
                  html.Div(id='graphs1')
                ],
              ),
            dcc.Tab(
                label='個股分析',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=TAB_STYLE,
                selected_style=SELECTED_STYLE,
                children=[ 
                  html.Div([
                    html.Div('資料日期：',style={'display': 'inline'}),
                    dcc.DatePickerRange(
                      id='date-picker-range2',
                      min_date_allowed=dt.datetime(2000, 1, 1),
                      max_date_allowed=dt.datetime(2100, 12, 31),
                      initial_visible_month=dt.datetime.now(),
                      display_format='M-D-Y',
                      end_date=dt.datetime.now(),
                      start_date=dt.datetime.now() - dt.timedelta(days=180) 
                    ),
                    html.Div('  股號:',style={'display': 'inline'}),
                    dcc.Input(
                      id="input2", 
                      type="text", 
                      placeholder="輸入股號", 
                      debounce=True,
                      style={'width': '120px', 
                             'height':'40px',
                             'font-size': 
                             '1.0em',
                             'margin-top': '0px',
                             'margin-bottom': '0px',
                             'paddingTop': 0,
                             'paddingBottom': 0,
                      },
                    ),
                  ]),
                  html.Div(id='graphs2')
                ]
            ),
            dcc.Tab(
                label='主力分析',
                value='tab-3', 
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=TAB_STYLE,
                selected_style=SELECTED_STYLE,
                children=[
                  html.Img(src=workingimg,
                    style={'display': 'inline',
                      'height': '200px',
                      'float': 'center'
                    }
                  ),
                  html.Div(id='graphs3')
                ]
            ),
            dcc.Tab(
                label='股票損益',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=TAB_STYLE,
                selected_style=SELECTED_STYLE,
                children=[
                  html.Img(src=workingimg,
                    style={'display': 'inline',
                      'height': '200px',
                      'float': 'center'
                    }
                  ),
                  html.Div(id='graphs4')
                ]
            ),
            dcc.Tab(
                label='出場警示',
                value='tab-5',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=TAB_STYLE,
                selected_style=SELECTED_STYLE,
                children=[
                  html.Img(src=workingimg,
                    style={'display': 'inline',
                      'height': '200px',
                      'float': 'center'
                    }
                  ),
                  html.Div(id='graphs5')
                ]
            ),
        ]
    )
],className="container")

# Stocks
st = StockTools()

def get_stock(date:str=None,force=False):

  start_date = dt.datetime.strptime(date,'%Y-%m-%d') - dt.timedelta(days=31)
  st.strdate = start_date.strftime('%Y-%m-%d')

  st.enddate = date
  print(st.strdate,st.enddate) 

  select = st.select(force)
  
  return select

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

def stock_figure(ticker):

    dff = st.read_stock(ticker)
    st._stock_anal(ticker)

    candlestick = [{
        'x': dff['date'],
        'open': dff['open'],
        'high': dff['high'],
        'low': dff['low'],
        'close': dff['close'],
        'type': 'candlestick',
        'name': ticker + ' ' +st.twse[ticker].name,
        'legendgroup': ticker + 'price',
        'increasing': {'line': {'color': colorscale1[0]}},
        'decreasing': {'line': {'color': colorscale1[-1]}}
    }]
   #bb_bands = bbands(dff.close)
   #bollinger_traces = [{
   #    'x': dff['date'], 'y': y,
   #    'type': 'scatter', 'mode': 'lines',
   #    'line': {'width': 1.3, 'color': colorscale2[(i*2) % len(colorscale2)]},
   #    'hoverinfo': 'y',
   #    'legendgroup': ticker + 'anal',
   #    'showlegend': True if i==0 False,
   #    'name': '{} - {}'.format(ticker,'bollinger')
   #} for i, y in enumerate(bb_bands)]
    ma_list = ['ma03','ma05','ma08','ma20','ma60']
    ma_traces = [{
        'x': dff['date'], 'y': st.ma_pd[ma],
        'type': 'scatter', 'mode': 'lines',
        'line': {'width': 1.5, 'color': colorscale2[(i*2) % len(colorscale2)]},
        'hoverinfo': 'name+y',
        'legendgroup': ticker + 'anal',
        'showlegend': True,
        'name': '{}'.format(ma)
    } for i, ma in enumerate(ma_list)]
    variation = [{
        'x': dff['date'], 'y': st.norstd,
        'type': 'scatter', 'mode': 'lines',
        'line': {'width': 1, 'color': colorscale2[2]},
        'hoverinfo': 'y',
        'legendgroup': ticker + 'norstd',
        'showlegend': True,
        'name': '{}'.format('變異係數'),
        'yaxis':'y2'
    }]

    graph = dcc.Graph(
          id=ticker,
          figure={
            'data': candlestick + ma_traces + variation,
            'layout': {
                'margin': {'b': 0, 'r': 60, 'l': 60, 't': 0},
                'legend': {'x': 0},
                'yaxis' : {'title':"價格"},
                'yaxis2': {'title':"變異係數",'anchor':"x",'overlaying':"y",'side':"right"}
            }
          }
      )

    return graph

@app.callback(
    [dash.dependencies.Output('stock-ticker-input','options'),
     dash.dependencies.Output('stock-ticker-input','value')],
    [dash.dependencies.Input('date-picker-single1', 'date'),
     dash.dependencies.Input('power-button1', 'on')])
def update_ticker(date,on):

    if date is not None:
      date = date[0:10]

    force = False
    if on:
      force = True

    select = get_stock(date,force)
    
    options = [{'label': 'BUY  '+s+' '+st.twse[s].name, 'value': str(s)} for s in select['buy']]
    options = options + [{'label': 'SELL '+s+' '+st.twse[s].name, 'value': str(s)} for s in select['sell']]   
    value = []
    if len(select['sell']) != 0: 
      value = [ select['sell'][0] ]
    if len(select['buy']) != 0: 
      value = [ select['buy'][0] ]
    return options, value

@app.callback(
    dash.dependencies.Output('graphs1','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('date-picker-range1', 'start_date'),
     dash.dependencies.Input('date-picker-range1', 'end_date')])
def update_graph(tickers,start_date, end_date):
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "選股中...",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
      if start_date is not None:
        st.strdate = start_date[0:10]
      if end_date is not None:
        st.enddate = end_date[0:10]

      for i, ticker in enumerate(tickers):
        graphs.append(stock_figure(ticker))

    return graphs

@app.callback(
    dash.dependencies.Output('graphs2', 'children'),
    [dash.dependencies.Input('date-picker-range2', 'start_date'),
     dash.dependencies.Input('date-picker-range2', 'end_date'),
     dash.dependencies.Input('input2', 'value')])
def update_output(start_date, end_date, stockid):
    graphs = []
    if start_date is None or end_date is None or stockid is None:
        graphs.append(html.H3(
            "請選擇正確的日期，且輸入股號。",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
      if start_date is not None:
        st.strdate = start_date[0:10]
      if end_date is not None:
        st.enddate = end_date[0:10]
      graphs.append(stock_figure(stockid))
      
    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)
