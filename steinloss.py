import sys

from src.Client import run as c_run
from src.Server import Server


class Steinloss:

    @staticmethod
    def server():
        one_second = 1
        server = Server(one_second)
        server.serve_packets()
        pass

    @staticmethod
    def client():
        c_run()

    @staticmethod
    def run():

        if len(sys.argv) > 1:
            Steinloss.server()
        else:
            Steinloss.client()

    pass


# socket = socket(AF_INET, SOCK_DGRAM)

Steinloss.run()
