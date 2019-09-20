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
app = dash.Dash()
server = app.server

app.scripts.config.serve_locally = False

colorscale2 = cl.scales['9']['qual']['Paired']
colorscale1 = cl.scales['9']['div']['RdYlGn']

# Stocks
st = StockTools()
st.strdate = dt.datetime.now() - dt.timedelta(days=31)
st.strdate = st.strdate.strftime('%Y-%m-%d')
st.enddata = dt.datetime.now().strftime('%Y-%m-%d')
select = st.select()
stocks = [select['sell']]

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/dash-stock-ticker-demo.csv')
logoimgsrc = "https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png"
logoimgsrc = "https://www.sccpre.cat/mypng/full/69-695057_background-images-hd-picsart-png-tiger-logo-clip.png"

app.layout = html.Div([
    html.Div(
      id='tabs-content-classes'
    ),
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
                children=[
                  html.Div([
                    html.H2('Taiwan Stock Tiger',
                    style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),
                    html.Img(src=logoimgsrc,
                      style={
                        'height': '100px',
                        'float': 'right'
                      },
                    ),
                  ]),
                  dcc.Dropdown(
                    id='stock-ticker-input',
                    options=[{'label': 'BUY '+s+' '+st.twse[s].name, 'value': str(s)} for s in select['buy']] +
                            [{'label': 'SELL '+s+' '+st.twse[s].name, 'value': str(s)} for s in select['sell']],
                    value=[  str(s) for s in select['buy']],
                    multi=True
                  ),
                  html.Div(id='graphs1')
                ],
              ),
            dcc.Tab(
                label='個股分析',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='主力分析',
                value='tab-3', 
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='股票損益',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ])
])

st.strdate = dt.datetime.now() - dt.timedelta(days=180)

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

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
