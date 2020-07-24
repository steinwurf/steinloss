import asyncio
import pickle
from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM

from src.util import repeat


class Probe:
    packet_size = 1024

    def __init__(self):
        self.log_port = 8888
        self.log_socket = socket(AF_INET, SOCK_STREAM)
        self.packets_received = []
        self.socket = socket(AF_INET, SOCK_DGRAM)

    async def main(self):
        logging_thread = asyncio.ensure_future(repeat(self.test_send_frontend, interval=1))
        recv_thread = asyncio.ensure_future(repeat(self.receive_packet))

        self.ping_server()

        await logging_thread
        await recv_thread

    def run(self):
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            pass
        finally:
            self.socket.close()
            self.log_socket.close()
            exit(1)

    async def receive_packet(self):
        packet = self.socket.recv(self.packet_size)
        self.packets_received.append((packet, datetime.now()))

    def encode_packets(self):
        return pickle.dumps(self.packets_received)

    def tcp_connect_to_server(self):
        self.log_socket.connect(('localhost', self.log_port))

    async def test_send_frontend(self):
        print(datetime.now().strftime("%H:%M:%S"))
        print(len(self.packets_received))
        # self.packets_received = []

    async def log_packets_to_server(self):
        encoded_msg = self.encode_packets()
        self.packets_received = []

        if self.log_socket is None:
            self.tcp_connect_to_server()

        self.log_socket.send(encoded_msg)

    def ping_server(self):
        address = '127.0.0.1', 7070
        self.socket.sendto('begin_test'.encode(), address)
