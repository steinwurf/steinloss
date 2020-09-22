import os
import pathlib

import dash
import pandas as pd
from plotly import graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard_util import format_to_graph_data

ONE_SECOND = 1000

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server
# app.config["suppress_callback_exceptions"] = True

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

probe_stats_full_path = os.path.join(APP_PATH, os.path.join("data", "client_stats_(1).csv"))
server_stats_full_path = os.path.join(APP_PATH, os.path.join("data", "server_stats_(8).csv"))
client_packets = pd.read_csv(probe_stats_full_path)
server_packets = pd.read_csv(server_stats_full_path)
result = client_packets.combine_first(server_packets)


@app.callback(Output('packet-loss', 'figure'),
              [Input('interval_component', 'n_intervals')])
def update_metrics(n):
    fig = generate_std_fig()
    server_values = pd.read_csv(server_stats_full_path)
    probe_values = pd.read_csv(probe_stats_full_path)

    loss_dataframe = format_to_graph_data(server_values, probe_values)

    fig.add_trace(go.Scatter(x=loss_dataframe.get('timestamp'), y=loss_dataframe.get('acc_loss'), name='packet loss'))

    return fig


@app.callback(Output('probe-received', 'figure'),
              [Input('interval_component', 'n_intervals')])
def update_metrics(n):  # noqa
    fig = generate_std_fig()
    fig.add_trace(go.Scatter(x=[0, 1, 2, 3], y=[4, 5, 6, 5], name='ping'))

    return fig


def render_banner_text():
    return html.Div(
        id="banner-text",
        children=[
            html.H5("Steinloss Dashboard"),
            html.H6("Packet measuring toolkit")
        ]
    )


def render_banner_logo():
    return html.Div(
        id="banner-logo",
        children=[
            html.A(
                html.Button(
                    id="learn-more-button",
                    children="Learn more"),
                href="https://www.steinwurf.com/"
            ),
            html.Img(
                id="logo",
                src=app.get_asset_url("steinwurf_logo_big_with_text.svg")
            )
        ]
    )


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            render_banner_text(),
            render_banner_logo()
        ]
    )


def build_packet_loss_gauge():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner('Grafik'),
            dcc.Graph(
                figure=go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=70,
                        title={
                            'text': 'packets recived',
                            'font': {
                                'color': 'white'}},
                        gauge={
                            'axis': {'range': [60, 100]},
                            'bgcolor': "white",
                            'steps': [
                                {'range': [95, 100], 'color': "green"},
                                {'range': [80, 95], 'color': "yellow"},
                                {'range': [0, 80], 'color': "red"}]
                        }

                    ),
                    go.Layout(
                        title='packet loss',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                ))
        ])


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def build_probe_recived_graph():
    return html.Div(
        id="probe-received-container",
        className="four columns",
        children=[
            generate_section_banner('Recived packets at probe'),
            dcc.Graph(
                id="probe-received",
                animate=True,
                figure=generate_std_fig()
            )
        ]
    )


def build_server_sent_graph():
    return html.Div(
        id="server-sent-container",
        className="four columns",
        children=[
            generate_section_banner('Sent packets from server'),
            dcc.Graph(
                id="server-sent",
                animate=True,
                figure=generate_std_fig()
            )
        ]
    )


def build_total_loss_graph():
    return html.Div(
        id="packet-loss-graph",
        className="eight columns",
        children=[
            generate_section_banner("Loss"),
            dcc.Graph(
                id="packet-loss",
                animate=True,
                figure=generate_std_fig()
            )
        ]
    )


def generate_std_fig(data=None):
    return go.Figure(
        data=data,
        layout=go.Layout(
            paper_bgcolor='rgba(0, 255, 255, 0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showline=False, showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, showline=False, zeroline=False),
            autosize=True
        ))


def build_graphs():
    return html.Div(
        id="graph-section-container",
        className="row",
        children=[
            build_probe_recived_graph(),
            # build_server_sent_graph(),
            build_total_loss_graph()]
    )


def build_status_container():
    return html.Div(
        id="status-container",
        children=[
            html.Div(
                id="graphs-container",
                children=[
                    build_packet_loss_gauge(),
                    build_graphs()
                ]

            )
        ]
    )


def build_interval():
    return dcc.Interval(
        id='interval_component',
        interval=30 * ONE_SECOND,
        n_intervals=0
    )


def build_dashboard():
    return html.Div(
        id="app-container",
        children=[
            html.Div(
                id="app-content",
                # TODO: tab implementation - render children at callback
                children=[
                    build_status_container(),
                    build_interval()])
        ]
    )


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        # dcc.Interval()
        build_dashboard()
    ])

app.run_server(debug=True, port=8050)
