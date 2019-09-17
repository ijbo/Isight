import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import base64
import datetime
import io
import pandas as pd
from app import app
import plotly.graph_objs as go
import dash_pivottable  as dpivot
import plotly.figure_factory as ff
import numpy as np
import plotly.express as px

children = list()
filename_data = list()
data_desc_list= list()
data_corr = list()
Excelsheet =list()
HeatMap_list = list()
scatter = list()
violin = list()
polar = list()
topo = list()
surface = list()


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
    html.Div(id='output-data-upload')
])


def parse_contents(contents, filename, date):
    #global df, df_desc, corr_matrix, fig, fig1, hist, app_list ,children ,polar , topo ,surface ,multiple ,ani
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    pl_colorscale = [[0.0, '#19d3f3'],
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
            #filenames = filename
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            for functions in [csv_data_display(df,filename), data_describe(df)
                              ,data_correlation(df),Excelsheet_ui(df) , Correlation_HeatMap(df),
                              Scatter_Plot(df), Violin_Plot(df)]:
                              #polar_chart(df),topographical_3d_surface(df), Surface_Plot_With_Contours(df)]:
                children.extend(functions)

        elif 'xls' in filename:
            #filenames = filename
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return html.Div(children)




def csv_data_display(df,filename):
    filename_data = [html.H5(filename),
        dcc.Interval(id='refresh', interval=200),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_as_list_view=True,
            # style_cell={'padding': '5px'},
            fixed_rows={'headers': True, 'data': 0},
            style_cell={'width': '150px'},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                # 'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }
        ),]
    return filename_data



def data_describe(df):

    df_desc = pd.concat([df.describe(include='all').fillna(0).round(),
                         df.isnull().sum().to_frame(name='missing').T,
                         df.dtypes.to_frame(name='dtype').T.astype(str)]).reset_index()

    data_desc_list=[html.H5("Data Describe : This method shows a summary of the numerical attributes"),
        dash_table.DataTable(
            data=df_desc.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.describe(include='all').reset_index().columns],
            style_as_list_view=True,
            style_cell={'padding': '15px'},
            fixed_rows={'headers': True, 'data': 0},
            fixed_columns={'headers': True, 'data': 1},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                'maxWidth': '1500px',
                'overflowX': 'scroll',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }
        ),]
    return data_desc_list




def data_correlation(df):
    #global data_corr
    corr_matrix = df.corr().reset_index()
    data_corr = [html.H5("Data Correlation: Statistical measure indicates the extent to which two or more variables fluctuate together"),
        dash_table.DataTable(
            # data=pd.concat([df.describe(include='all').fillna(0).round().reset_index(),df.isnull().sum().to_frame(name = 'missing').T.reset_index()]).to_dict('records'),
            data=corr_matrix.reset_index().to_dict('records'),
            columns=[{'name': i, 'id': i} for i in corr_matrix.reset_index().columns],
            style_as_list_view=True,
            style_cell={'padding': '15px'},
            fixed_rows={'headers': True, 'data': 0},
            fixed_columns={'headers': True, 'data': 1},
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'},
            style_table={
                'maxHeight': '300px',
                'maxWidth': '1500px',
                'overflowX': 'scroll',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            }
        ),]

    return data_corr


def Excelsheet_ui(df):
    Excelsheet = [html.H5("Create Excelsheet for data"),
        dpivot.PivotTable(
            id='table',
            data=df.to_dict('records'),
            cols=[i for i in df.columns],
            colOrder="key_a_to_z",
            rows=[],
            rowOrder="key_a_to_z",
            rendererName="Grouped Column Chart",
            aggregatorName="Average",
            vals=[],
            valueFilter={}
        ),]
    return Excelsheet

def Correlation_HeatMap(df):
    #global HeatMap_list


    HeatMap_list = [html.H5("Correlation HeatMap"),
        dcc.Graph(
            id='heatmap',
            figure={
                'data': [{
                    'z': df[df.select_dtypes(include=[np.number]).columns].corr().values,
                    'x': list(df.select_dtypes(include=[np.number]).columns),
                    'y': list(df[df.select_dtypes(include=[np.number]).columns].corr().index),
                    'text': [df[df.select_dtypes(include=[np.number]).columns].corr().round(2).values],
                    'type': 'heatmap',
                    'colorscale': 'Viridis'

                }],
                'layout': {
                    'height': 800,
                    'width': "100%",

                    'colorscale': 'Viridis',
                    'margin': {
                        'l': 200,
                        'r': 100,
                        'b': 150,
                        't': 100
                    }
                    }
            }
        ),]
    return HeatMap_list




def Scatter_Plot(df):
    #scatter=[html.H5("Scatter Plot"),
    #    dcc.Graph(id='scatter plot', figure=px.scatter_matrix(df[df.select_dtypes(include=[np.number]).columns])),]
    scatter=[html.H5("scatter matrix"),
    dcc.Graph(id='scatter matrix', figure=px.scatter_matrix(df, dimensions=list(df.columns),
                                                                color="ocean_proximity", symbol="ocean_proximity",
                                                                 width=1500, height=1500))]
        #           ),]
    return scatter


def Violin_Plot(df):
    # global violin
    # global children
    fig = go.Figure()
    for col in list(df.select_dtypes(include=[np.number]).columns):
        fig.add_trace(go.Violin(x0=col,
                                y=(df[col] - df[col].mean()) / df[col].std(),
                                name=col,
                                box_visible=True,
                                meanline_visible=True))

    fig1 = go.Figure()
    for col in list(df.select_dtypes(include=[np.number]).columns):
        fig1.add_trace(go.Violin(x0=col,
                                 y=(df[col] - df[col].min()) / (df[col].max() - df[col].min()),
                                 name=col,
                                 box_visible=True,
                                 meanline_visible=True))

    violin = [html.H5("Violin Plot:Outlier plot with mean normalization"),
        dcc.Graph(figure=fig),
        html.H5("Violin Plot:Outlier plot with min-max normalization"),
        dcc.Graph(figure=fig1),]
    return violin


def polar_chart(df):
    # global polar
    # global children
    pol = go.Figure()
    for col in list(df.select_dtypes(include=[np.number]).columns):
        pol.add_trace(go.Scatterpolargl(
            r=df[col],
            # theta = df[col],
            name=col,
            marker=dict(size=15, color="mediumseagreen")))
    polar = [html.H5("Polar Chart"),dcc.Graph(figure=pol)]

    return polar


def topographical_3d_surface(df):
    # global topo
    # global children
    top = go.Figure(data=[go.Surface(z=df.values)])
    top.update_layout(title="3d graph", autosize=False,
                       width=500, height=500,
                       margin=dict(l=65, r=50, b=65, t=90))
    topo= [
        html.H5("Topographical 3D Surface Plot"),
        dcc.Graph(figure=top),]
    return topo


def Surface_Plot_With_Contours(df):
    # global surface
    # global children
    #global filename
    sur = go.Figure(data=[go.Surface(z=df.values)])
    sur.update_traces(contours_z=dict(show=True, usecolormap=True,
                                          highlightcolor="limegreen", project_z=True))
    sur.update_layout(title="Contour Plot", autosize=False,
                          scene_camera_eye=dict(x=1.87, y=0.88, z=-0.64),
                          width=500, height=500,
                          margin=dict(l=65, r=50, b=65, t=90))

    surface = [html.H5(" Surface Plot With Contours"),
        dcc.Graph(figure=sur),]
    return surface



@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    #global df, df_desc, corr_matrix, fig, fig1, hist,  filename ,children ,polar , topo ,surface ,multiple ,ani
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        # children.append(n_clicks)
        return children


























