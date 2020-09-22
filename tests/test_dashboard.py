import pandas as pd


class Test_Dashboard:
    def setup_method(self):
        self.server_values = pd.read_csv('test_server.csv')
        self.client_values = pd.read_csv('test_client.csv')
