import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import dash_table
import base64
import datetime
import io
import pandas as pd
from app import app
import plotly.graph_objs as go

import numpy as np

x = np.arange(10)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    pl_colorscale=[[0.0, '#19d3f3'],
               [0.333, '#19d3f3'],
               [0.333, '#e763fa'],
               [0.666, '#e763fa'],
               [0.666, '#636efa'],
               [1, '#636efa']]
    axis = dict(showline=True,
          zeroline=False,
          gridcolor='#fff',
          ticklen=4)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            output = io.StringIO()
            df.info(buf=output)
            df_info = pd.DataFrame(columns=['Col'], data=output.getvalue().split('\n'))
            #val =  [ i for i in df_info[2:].Col[2:]]
            df_desc = pd.concat([df.describe(include='all').fillna(0).round(),
            df.isnull().sum().to_frame(name = 'missing').T,
            df.dtypes.to_frame(name = 'dtype').T.astype(str)]).reset_index()
            #print(df_desc)
            corr_matrix = df.corr().reset_index()
            #print(corr_matrix)
            classes=np.unique(df['ocean_proximity'].values).tolist()
            class_code={classes[k]: k for k in range(len(classes))}
            color_vals=[class_code[cl] for cl in df['ocean_proximity'].astype(str)]
            #text=[df.loc[ k, 'ocean_proximity'] for k in len(df)]
            index_vals = df['ocean_proximity'].astype('category').cat.codes
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([
        html.H5(filename),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_as_list_view=True,
            #style_cell={'padding': '5px'},
            fixed_rows={ 'headers': True, 'data': 0 },
            style_cell={'width': '150px'},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                #'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }   
        ),
        html.H5("Data Describe : This method shows a summary of the numerical attributes"),
        dash_table.DataTable(
            #data=pd.concat([df.describe(include='all').fillna(0).round().reset_index(),df.isnull().sum().to_frame(name = 'missing').T.reset_index()]).to_dict('records'),
            data=df_desc.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.describe(include='all').reset_index().columns],
            style_as_list_view=True,
            style_cell={'padding': '15px'},
            fixed_rows={ 'headers': True, 'data': 0 },
            fixed_columns={ 'headers': True, 'data': 1 },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                'maxWidth' : '1500px',
                'overflowX': 'scroll',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }   
        ),
         html.H5("Data Correlation"),
        dash_table.DataTable(
            #data=pd.concat([df.describe(include='all').fillna(0).round().reset_index(),df.isnull().sum().to_frame(name = 'missing').T.reset_index()]).to_dict('records'),
            data=corr_matrix.reset_index().to_dict('records'),
            columns=[{'name': i, 'id': i} for i in corr_matrix.reset_index().columns],
            style_as_list_view=True,
            style_cell={'padding': '15px'},
            fixed_rows={ 'headers': True, 'data': 0 },
            fixed_columns={ 'headers': True, 'data': 1 },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                'maxWidth' : '1500px',
                'overflowX': 'scroll',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }   
        ),
        dcc.Graph(
        id='SPloM',
        config={
            'showSendToCloud': True,
            #'plotlyServerURL': 'https://plot.ly'
        },
        figure={
            'data': [go.Scatter(x=df["longitude"], y=df["latitude"],mode='markers',)]
        }
        ),
        dcc.Graph(
        id='SPloM-selectedPoints',
        config={
            'showSendToCloud': True,
            #'plotlyServerURL': 'https://plot.ly'
        },
        figure={
            'data': [go.Splom(dimensions=[dict(label='median_house_value',
                                 values=df['median_house_value']),
                            dict(label='median_income',
                                 values=df['median_income']),
                            dict(label='total_rooms',
                                 values=df['total_rooms']),
                            dict(label='housing_median_age',
                                 values=df['housing_median_age'])
                           ],
                text=None,
                #default axes name assignment :
                #xaxes= ['x1','x2',  'x3'],
                #yaxes=  ['y1', 'y2', 'y3'], 
                marker=dict(color=index_vals,
                            showscale=False, # colors encode categorical variables
                            line_color='white', line_width=0.5)
                )],
            
                },
                ),
        html.Hr()  # horizontal line
        # For debugging, display the raw contents provided by the web browser
])

layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
        