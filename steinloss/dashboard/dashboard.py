import random
from datetime import datetime, timedelta
from hurry.filesize import size, verbose

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy
import plotly
from dash.dependencies import Input, Output

from steinloss.Data_Presenter import Data_Presenter
from steinloss.loss_calculator import TimeTable

loss = 'loss'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('TERRA Satellite Live Feed'),
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

    timestamp = datetime.now() - timedelta(seconds=1)
    time_entry = time_table[timestamp]

    speed = size(time_entry.sent * 1024, system=verbose)

    return [
        html.Span(f"Package speed: {speed}/s", style=style),
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = {
        'time': [],
        loss: [],
    }

    # Collect some data
    data_from_presenter = TimeTable()
    time = datetime.now()
    for x in range(0, 180):
        delta = timedelta(seconds=x)
        timestamp = time - delta

        data_from_presenter[timestamp].sent = random.randint(90, 180)
        data_from_presenter[timestamp].received = random.randint(1, 90)
        data_from_presenter[timestamp].loss = data_from_presenter[timestamp].received / data_from_presenter[
            timestamp].sent

    data_presenter = Data_Presenter.get_instance()
    time_table = data_presenter.get_time_table()
    base = datetime.now()

    timestamp_array = numpy.array([base - timedelta(seconds=i) for i in range(1, 180)])
    for d in timestamp_array:
        data['time'].append(d)

        loss_pct = 0
        entry = time_table[d]
        if entry.sent != 0:
            loss_pct = entry.loss / time_table[d].sent
        data[loss].append(loss_pct)

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data[loss],
        'name': loss,
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    return fig


def run():
    app.run_server(host='127.0.0.1', port=8050)


if __name__ == '__main__':
    run()
