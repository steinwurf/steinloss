from matplotlib import markers, style
from matplotlib.pyplot import margins
import plotly.graph_objects as go
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

from steinloss.DataCollection import DataCollection

app = dash.Dash(__name__, external_stylesheets=['steinloss/dashboard/assets/bootstrap.min.css'])

app.title = "Steinloss Dashboard"

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Steinloss', style={'backgroundColor':'#6AB187', 'textAlign':'center', 'color':'black'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='lost-percent-graph')
            ], width=8, style={'margin-right':'10px', 'margin-left':'20px', 'margin-top':'10px', 'margin-bottom':'10px'}),
            dbc.Col([
                html.Div([
                    html.H3('Status Report', style={'textAlign':'center', 'color':'black'}),
                    html.P(html.Span(id='status-report'))], 
                    style={'backgroundColor':'white', 'margin-right':'10px', 'margin-left':'0px', 'margin-top':'10px', 'margin-bottom':'10px'}
                ),
                html.Div([dbc.Button(id='download_button_time', children=['Download time data']), dcc.Download(id='download_component_time')]),
                html.Div([dbc.Button(id='download_button_packet', children=['Download packet data']), dcc.Download(id='download_component_packet')])]
            , width=3)
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='cons_lost_packets')
            ], width=8, style={'margin-right':'10px', 'margin-left':'20px', 'margin-top':'10px', 'margin-bottom':'10px'}),
            dbc.Col([
                # Empty column
            ], width=3)
        ]),

        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]),
])

@app.callback(Output('lost-percent-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_lost_prc_graph(n):
    # Retrieve some data
    data_collection = DataCollection()
    df = data_collection.retrieve_lost_percentage_over_time()

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['loss'], name='Lost packages', marker=dict(color='#6AB187')))

    fig.update_layout(
        title='Percent of Lost Packages Over Time',
        xaxis_title='Time',
        yaxis_title='Package Loss (%)',
        margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ))

        #paper_bgcolor='rgba(0,0,0,0)',
        #plot_bgcolor='rgba(0,0,0,0)'

    return fig

@app.callback(Output('cons_lost_packets', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_cons_lost_packets(n):
    data_collection = DataCollection()
    df_consecutive_lost_packets = data_collection.get_consecutive_packets_lost_df()

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df_consecutive_lost_packets['lost_cons_packets'],
                            y=df_consecutive_lost_packets['normalized_count'],
                            marker=dict(color='#6AB187'))
    )
    fig.update_layout(
        title='Bar chart of how many packets is lost consecutively',
        xaxis_title='Number of consecutive lost packets',
        yaxis_title='Frequency',
        margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ))

    return fig


@app.callback(Output('status-report', 'children'),
              Input('interval-component', 'n_intervals'))
def update_status(n):
    style = {'padding': '10px', 'display': 'inline-block'}

    data_collection = DataCollection()

    server_status, probe_status, sent_packets, recv_packets, latency, speed = data_collection.get_status_report()

    return [
        html.Span([f'Server status: {server_status}',
                    html.Br(),
                    f'Probe status: {probe_status}',
                    html.Br(),
                    f'Sent packets: {sent_packets}',
                    html.Br(),
                    f'Recieved packets: {recv_packets}',
                    html.Br(),
                    f'Latency: {latency} ms',
                    html.Br(),
                    f'Speed: {speed}'], style=style)
    ]

@app.callback(Output('download_component_time', 'data'),
              Input('download_button_time', 'n_clicks'),
              prevent_initial_call=True)
def download_data(n_clicks):
    data_collection = DataCollection()
    df = data_collection.retrieve_lost_percentage_over_time()

    return dcc.send_data_frame(df.to_csv, "packet_time_data.csv")


@app.callback(Output('download_component_packet', 'data'),
              Input('download_button_packet', 'n_clicks'),
              prevent_initial_call=True)
def download_data(n_clicks):
    data_collection = DataCollection()
    df = data_collection.retrieve_individual_packet_df_from_seconds()

    df.drop(['sent_at', 'recieved_at'], inplace=True, axis=1)

    dict1 = {1:1, 2:2}
    #return dcc.send_data_frame(df.to_json, "packet_time_data.json", orient='records')
def run():
    app.run_server(host='0.0.0.0', port=8050, debug=True)


if __name__ == '__main__':
    run()
