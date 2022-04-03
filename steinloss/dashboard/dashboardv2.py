from ast import Div
from distutils.log import debug
from pickle import TRUE
from matplotlib import style
from matplotlib.pyplot import margins
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import numpy
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_daq as daq
from steinloss.utilities import log
from steinloss.DataCollection import DataCollection

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Steinloss Dashboard"

server = app.server

app.layout = html.Div(
    [
        html.H1('Steinloss Dashboard', style= {'backgroundColor' : '#6AB187', 'textAlign' : 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='cons_packet_graph')),
                dbc.Col(daq.Gauge(
                id='1gauge',
                value=5,
                label='Speed',
                showCurrentValue=True,
                max=20,
                min=0
                )),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='lost-percent-graph')),
                dbc.Col(daq.Gauge(
                id='gauge',
                value=5,
                label='Speed',
                showCurrentValue=True,
                max=20,
                min=0)),
            ]
        ),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]
)
    

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

@app.callback(Output('gauge', 'value'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    data_collection = DataCollection()
    speed = data_collection.get_actual_package_speed()

    return float(speed)


def run():
    app.run_server(host='0.0.0.0', port=8050, debug=True)


if __name__ == '__main__':
    run()
