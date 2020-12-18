from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy
import plotly.express as px
from dash.dependencies import Input, Output
from hurry.filesize import size, verbose

from steinloss.Data_Presenter import Data_Presenter

TIME = 'TIME'

LOSS = 'loss'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    html.Div([
        html.H4('Steinloss: package loss'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        )
    ])
)

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
            loss_decimal = entry.loss / time_table[timestamp].sent
        loss_pct = loss_decimal * 100
        data[LOSS].append(loss_pct)

    # Create the graph
    fig_2 = px.line(data, x=TIME, y=LOSS, title="Loss",
                    labels={
                        LOSS: 'package loss (%)',
                        TIME: 'Timestamp'
                    })
    return fig_2


def run():
    app.run_server(host='0.0.0.0', port=8050)


if __name__ == '__main__':
    run()
