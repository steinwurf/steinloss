import math
from datetime import datetime

import pandas as pd
from typing import List

from src.packet_entity import Packet_entity


def format_to_graph_data(server_values: pd.DataFrame, probe_values: pd.DataFrame):
    x = server_values.set_index('packet').join(probe_values.set_index('packet'), lsuffix='_server', rsuffix='_probe')

    graph_data = []
    loss = 0
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    for row in x.itertuples():
        if isinstance(row.timestamp_probe, str):
            ping = datetime.strptime(row.timestamp_probe, fmt) - datetime.strptime(row.timestamp_server, fmt)
        else:
            loss += 1
            ping = 0
        graph_data.append((row.timestamp_server, loss / row.Index, ping))
    graph_dataframe = pd.DataFrame(graph_data, columns=['timestamp', 'acc_loss', 'ping'])
    return graph_dataframe
