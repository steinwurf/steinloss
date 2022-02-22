import imp
import urllib.parse
from copy import copy
from datetime import datetime, timedelta

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

""" from steinloss import log
from steinloss.Data_Presenter import Data_Presenter """

from Data_Presenter import Data_Presenter
from utilities import log

TIME = 'TIME'

LOSS = 'loss'
PACKET_COUNT = 'loss-count'
PACKET_TYPE = 'sent-count'

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H4('Steinloss: package loss'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='lost-percent-graph'),
        dcc.Graph(id='lost-sent-graph'),
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
    data_presenter = Data_Presenter.get_instance()
    time_table = data_presenter.get_time_table()

    timestamp = datetime.now() - timedelta(seconds=15)
    time_entry = time_table[timestamp]

    speed = size(time_entry.sent * 1024, system=verbose)

    return [
        html.Span(f"Actual package speed: {speed}/s", style=style),
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('lost-percent-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = {
        TIME: [],
        LOSS: [],
    }

    # Collect some data
    data_presenter = Data_Presenter.get_instance()
    time_table = data_presenter.get_time_table()
    base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

    timestamp_array = numpy.array([base - timedelta(seconds=i) for i in range(1, 180)])
    for timestamp in timestamp_array:
        data[TIME].append(timestamp)

        loss_decimal = 0
        entry = time_table[timestamp]
        if entry.sent != 0:
            loss_decimal = entry.loss / entry.sent
        loss_pct = loss_decimal * 100
        data[LOSS].append(loss_pct)

    df = pd.DataFrame.from_dict(data)
    # Create the graph
    fig = px.line(df, x=TIME, y=LOSS, title="Loss",
                    labels={
                        LOSS: 'Package loss (%) ',
                        TIME: 'Timestamp ',
                    })
    return fig


@app.callback(Output('lost-sent-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_sent_lost(n):
    data = {
        TIME: [],
        PACKET_TYPE: [],
        PACKET_COUNT: []
    }

    # Collect some data
    data_presenter = Data_Presenter.get_instance()
    time_table = data_presenter.get_time_table()
    base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

    timestamp_array = numpy.array([base - timedelta(seconds=i) for i in range(1, 180)])
    for timestamp in timestamp_array:
        entry = time_table[timestamp]

        data[TIME].append(timestamp)
        data[PACKET_COUNT].append(entry.sent - entry.loss)
        data[PACKET_TYPE].append('received')

        data[TIME].append(timestamp)
        data[PACKET_COUNT].append(entry.sent)
        data[PACKET_TYPE].append('sent')

    df = pd.DataFrame.from_dict(data)


    # Create the graph
    fig = px.line(df, x=TIME, y=PACKET_COUNT, title="Sent/Received", color=PACKET_TYPE,
                    labels={
                        PACKET_COUNT: 'Packets: ',
                        TIME: 'Timestamp ',
                        PACKET_TYPE: 'Type: '
                    })
    return fig

@app.callback(Output('download_component', 'data'),
              Input('download_button', 'n_clicks'),
              prevent_initial_call=True)
def download_data(n_clicks):
    data = {
        TIME: [],
        LOSS: [],
    }

    # Collect some data
    data_presenter = Data_Presenter.get_instance()
    time_table = data_presenter.get_time_table()
    base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

    timestamp_array = numpy.array([base - timedelta(seconds=i) for i in range(1, 180)])
    for timestamp in timestamp_array:
        data[TIME].append(timestamp)

        loss_decimal = 0
        entry = time_table[timestamp]
        if entry.sent != 0:
            loss_decimal = entry.loss / entry.sent
        loss_pct = loss_decimal * 100
        data[LOSS].append(loss_pct)

    df = pd.DataFrame.from_dict(data)

    return dcc.send_data_frame(df.to_csv, "package_data.csv")

def run():
    app.run_server(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run()
