#!/usr/bin/env python 
from stocktools import StockTools
import dash
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
# Stocks
st = StockTools()

# dash 
app = dash.Dash(__name__)
server = app.server

app.scripts.config.serve_locally = False
app.config.suppress_callback_exceptions=True
app.title = 'Tiger'    

colorscale2 = cl.scales['9']['qual']['Paired']
colorscale1 = cl.scales['9']['div']['RdYlGn']

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/dash-stock-ticker-demo.csv')
logoimgsrc = "https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png"
logoimgsrc = "https://www.sccpre.cat/mypng/full/69-695057_background-images-hd-picsart-png-tiger-logo-clip.png"

def get_stock(date:str=None):
  if date == None:
    st.strdate = dt.datetime.now() - dt.timedelta(days=31)
    st.strdate = st.strdate.strftime('%Y-%m-%d')
    st.enddate = dt.datetime.now().strftime('%Y-%m-%d')
  else:
    st.strdate = dt.datetime.strptime(date,'%Y-%m-%d') - dt.timedelta(days=31)
    st.strdate = st.strdate.strftime('%Y-%m-%d')
    st.enddate = date        
    print(st.strdate,st.enddate) 
  select = st.select()
  return select

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
                    dcc.DatePickerSingle(
                      id='date-picker-single',
                      min_date_allowed=dt.datetime(2000, 1, 1),
                      max_date_allowed=dt.datetime(2100, 12, 31),
                      initial_visible_month=dt.datetime.now(),
                      date=dt.datetime.now().strftime('%Y-%m-%d'),
                      display_format='DD-MMM-YYYY',
                      clearable=True,
                      with_portal=True,
                    ),
                  ]),
                  html.Div([
                    dcc.Dropdown(
                      id='stock-ticker-input',
                      multi=True
                    )
                  ]),
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
                  html.Div(id='graphs5')
                ]
            ),
        ]
    )
],className="container")

st.strdate = dt.datetime.now() - dt.timedelta(days=180)

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

@app.callback(
    [dash.dependencies.Output('stock-ticker-input','options'),
     dash.dependencies.Output('stock-ticker-input','value')],
    [dash.dependencies.Input('date-picker-single', 'date')])
def update_ticker(date):
    select = get_stock(date)

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
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        st.strdate = dt.datetime.strptime(st.enddate,'%Y-%m-%d') - dt.timedelta(days=180)
        st.strdate = st.strdate.strftime('%Y-%m-%d')

        for i, ticker in enumerate(tickers):

            #dff = df[df['Stock'] == ticker]
            dff = st.read_stock(ticker)

            candlestick = [{
                'x': dff['date'],
                'open': dff['open'],
                'high': dff['high'],
                'low': dff['low'],
                'close': dff['close'],
                'type': 'candlestick',
                'name': ticker + ' ' +st.twse[ticker].name,
                'legendgroup': st.twse[ticker].name,
                'increasing': {'line': {'color': colorscale1[0]}},
                'decreasing': {'line': {'color': colorscale1[-1]}}
            }]
            bb_bands = bbands(dff.close)
            bollinger_traces = [{
                'x': dff['date'], 'y': y,
                'type': 'scatter', 'mode': 'lines',
                'line': {'width': 1, 'color': colorscale2[(i*2) % len(colorscale2)]},
                'hoverinfo': 'none',
                'legendgroup': ticker,
                'showlegend': True if i == 0 else False,
                'name': '{} - bollinger bands'.format(ticker)
            } for i, y in enumerate(bb_bands)]
            graphs.append(
                dcc.Graph(
                  id=ticker,
                  figure={
                    'data': candlestick + bollinger_traces,
                    'layout': {
                        'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                        'legend': {'x': 0}
                    }
                  }
                )
            )

    return graphs


if __name__ == '__main__':
    app.run_server(debug=True)
