import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd


import sys
import os

print(os.getcwd())

sys.path.append('D:/ML/Anaconda/envs/Isight/src/')

from app import app
from apps import app1, app2


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Go to upload', href='/apps/app1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/apps/app2'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True,port=8889)