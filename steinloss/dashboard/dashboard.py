import urllib.parse

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
from steinloss.Data_Presenter import Data_Presenter

TIME = 'TIME'

LOSS = 'loss'
LOSS_COUNT = 'loss-count'

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H4('Steinloss: package loss'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
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
        LOSS_COUNT: []
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

        data[LOSS_COUNT].append(f' {entry.loss}/{entry.sent}')

    # Create the graph
    fig_2 = px.line(data, x=TIME, y=LOSS, title="Loss", color=LOSS_COUNT,
                    labels={
                        LOSS: 'Package loss (%) ',
                        TIME: 'Timestamp ',
                        LOSS_COUNT: 'Lost/Sent '
                    })
    return fig_2


@app.callback(Output('file-list', 'children'),
              [Input('save-data-btn', 'n_clicks')],
              [State('file-list', 'children')])
def save_data(n_clicks, old_output):
    if n_clicks == 0:
        raise PreventUpdate

    data_presenter = Data_Presenter.get_instance()
    packet_table = data_presenter.get_packet_table()
    dataframe = pd.DataFrame(data=packet_table, columns=['sent_at', 'received_at'])

    csv_string = dataframe.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

    file_name = f'loss_data_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.csv'
    download_link = html.A(
        file_name,
        id='download-link',
        download=file_name + ".csv",
        href=csv_string,
        target="_blank"
    )

    list_item = html.Li(download_link)
    return old_output + [list_item]


def run():
    app.run_server(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run()
