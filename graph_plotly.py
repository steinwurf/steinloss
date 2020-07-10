import pandas as pd
import dash
import pandas as pd
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

client_packets = pd.read_csv("client_stats.csv")
server_packets = pd.read_csv("server_stats.csv")
result = client_packets.combine_first(server_packets)

fig = px.line(result)
fig.show()
