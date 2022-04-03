

#df = pd.read_csv('/home/jeppe/Downloads/packet_data(1).csv')
from ast import Div
from distutils.log import debug
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


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = "Steinloss Dashboard"


server = app.server

app.layout= html.Div(
    [
        html.H1('Steinloss Dashboard', style= {'backgroundColor' : '#6AB187', 'textAlign' : 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='cons_packet_graph'), width=8),
                dbc.Col(daq.Gauge(
                id='1gauge',
                value=5,
                label='Speed',
                showCurrentValue=True,
                max=20,
                min=0), width=4),
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
def run():
    app.run_server(host='0.0.0.0', port=8050, debug=True)
run()