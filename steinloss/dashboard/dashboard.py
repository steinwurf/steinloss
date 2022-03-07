import imp
import urllib.parse
from copy import copy
from datetime import datetime, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from hurry.filesize import size, verbose

from steinloss.utilities import log
from steinloss.DataCollection import DataCollection

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H4('Steinloss: package loss'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='lost-percent-graph'),
        dcc.Graph(id='lost-sent-graph'),
        dcc.Graph(id='distribution'),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]),

    html.Div([dbc.Button(id='download_button', children=['Download data']), dcc.Download(id='download_component')]),
])

start = datetime.now()


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '16px'}

    data_collection = DataCollection()
    speed = data_collection.get_actual_package_speed()

    return [
        html.Span(f"Actual package speed: {speed}/s", style=style),
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('lost-percent-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    # Retrieve some data
    data_collection = DataCollection()
    df = data_collection.retrieve_lost_percentage_over_time()

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['loss'], name='Lost packages'))

    fig.update_layout(
        title='Percent of Lost Packages Over Time',
        xaxis_title='Time',
        yaxis_title='Package Loss (%)')

    return fig


@app.callback(Output('lost-sent-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_sent_lost(n):
    data_collection = DataCollection()
    df = data_collection.retrieve_sent_recieved_packets_df()

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['sent-count'], name='Sent'))
    fig.add_trace(go.Scatter(x=df['time'], y=df['recieved-count'], name='Recieved'))

    fig.update_layout(
        title='Count of Sent and Recieved Packages',
        xaxis_title='Time',
        yaxis_title='Number of Packages')

    return fig


@app.callback(Output('download_component', 'data'),
              Input('download_button', 'n_clicks'),
              prevent_initial_call=True)
def download_data(n_clicks):
    data_collection = DataCollection()
    df = data_collection.retrieve_lost_percentage_over_time()

    return dcc.send_data_frame(df.to_csv, "package_data.csv")


@app.callback(Output('distribution', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_distributions(n):
    data_collection = DataCollection()
    df_sent_recieved = data_collection.retrieve_sent_recieved_packets_df()
    df_loss_pct = data_collection.retrieve_lost_percentage_over_time()

    # The first datapoints arent relavent due to the server starting up.
    df_sent_recieved_filtered = df_sent_recieved[df_sent_recieved['sent-count'] > 800]
    df_loss_pct_filtered = df_loss_pct[df_loss_pct['loss'] > 0]
    
    fig = make_subplots(rows=1,
                        cols=3,
                        subplot_titles=['Packet Loss in Percent', 'Count of Recieved Packets', 'Count of Sent Packets'])

    # lost-pct
    fig.add_trace(go.Histogram(x=df_loss_pct_filtered['loss'],
                               histnorm='probability'), 
                  row=1, 
                  col=3)

    # recieved
    fig.add_trace(go.Histogram(x=df_sent_recieved_filtered['recieved-count'],
                                    histnorm='probability'),
                  row=1,
                  col=2)

    # sent histogram:
    fig.add_trace(go.Histogram(x=df_sent_recieved_filtered['sent-count'],
                                    histnorm='probability'), 
                  row=1,
                  col=1)

    fig.update_layout(showlegend=False)
    return fig


def run():
    app.run_server(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run()
