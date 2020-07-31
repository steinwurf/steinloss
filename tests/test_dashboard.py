from dashboard_util import format_to_graph_data
import pandas as pd
import numpy as np


class Test_Dashboard:
    def setup_method(self):
        self.server_values = pd.read_csv('test_server.csv')
        self.client_values = pd.read_csv('test_client.csv')
