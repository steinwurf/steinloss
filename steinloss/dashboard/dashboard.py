import urllib.parse
from copy import copy

from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from hurry.filesize import size, verbose
import pandas as pd

from steinloss import log
from steinloss.Data_Presenter import Data_Presenter

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
        dcc.Graph(id='live-update-graph'),
        dcc.Graph(id='lost-sent-graph'),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]),

    html.Div(id='save-data',
             children=[
                 html.Button("download data", id='save-data-btn', n_clicks=0),
                 html.Ul(id='file-list', children=[])
             ]),
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
@app.callback(Output('live-update-graph', 'figure'),
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

    # Create the graph
    fig_2 = px.line(data, x=TIME, y=LOSS, title="Loss",
                    labels={
                        LOSS: 'Package loss (%) ',
                        TIME: 'Timestamp ',
                    })
    return fig_2


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

    # Create the graph
    fig_2 = px.line(data, x=TIME, y=PACKET_COUNT, title="Sent/Received", color=PACKET_TYPE,
                    labels={
                        PACKET_COUNT: 'Packets: ',
                        TIME: 'Timestamp ',
                        PACKET_TYPE: 'Type: '
                    })
    return fig_2


def prep_data(packet_table):
    packet_table = copy(packet_table)
    return map(lambda entry: [packet_table[entry].sent_at.strftime("%Y-%m-%d_%H:%M:%S"),
                              packet_table[entry].received_at.strftime("%Y-%m-%d_%H:%M:%S") if packet_table[
                                  entry].received_at else ''], 
                                packet_table)


@app.callback(Output('file-list', 'children'),
              [Input('save-data-btn', 'n_clicks')],
              [State('file-list', 'children')])
def save_data(n_clicks, old_output):
    if n_clicks == 0 or n_clicks == 1:
        raise PreventUpdate

    data_presenter = Data_Presenter.get_instance()
    packet_table = data_presenter.get_packet_table()
    dataframe = pd.DataFrame(columns=['sent_at', 'received_at'])
    try:
        for x in [['a', 'b']]:  # prep_data(packet_table):
            dataframe.append({'sent_at': x[0], 'received_at': x[1]}, ignore_index=True)

        csv_string = dataframe.to_csv(index=False,
                                      encoding='utf-8')

        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

        file_name = f'loss_data_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.csv'
        download_link = html.A(
            file_name,
            id='download-link',
            download=file_name + ".csv",
            href=csv_string,
            target="_blank"
        )
    except RuntimeError as e:
        log(e)
        download_link = html.P('The test is not finished yet. Wait for the test to finish')

    list_item = html.Li(download_link)

    return old_output + [list_item]


def run():
    app.run_server(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run()
