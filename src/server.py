import asyncio
import socket
from datetime import datetime
from typing import Tuple
import time
from src.entity_logger import Entity_Logger
from src.packet_entity import Packet_entity

ONE_SECOND = 1

kilobyte = 1024
megabyte = 1024 * kilobyte
gigabyte = 1048576 * kilobyte


class Server:
    packet_size = kilobyte

    @classmethod
    def gigabyte(cls):
        return cls(speed=gigabyte)

    def __init__(self, speed=megabyte, listening_address=('0.0.0.0', 7070),
                 runtime_of_test=ONE_SECOND * 60 * 2):
        self.last_sent_packet = 0
        self.last_received_packet = 0
        self.time_of_sample_size = runtime_of_test
        self.socket_timeout = 10  # seconds
        self.log_interval = 1
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listening_address = listening_address
        self.outgoing_packets = []
        self.incoming_packets = []
        self.id = 0
        self.__interval = 1
        self.speed = speed

    @property
    def speed(self):
        return 1 / self.__interval * self.packet_size

    @speed.setter
    def speed(self, value):
        self.__interval = self.packet_size / value

    @property
    def interval(self):
        return self.__interval

    def send_packet(self, address):
        packet = "%d" % self.id
        self.server_socket.sendto(packet.encode(), address)

        self.id += 1
        self.save_entry()

    def save_entry(self):
        self.outgoing_packets.append(Packet_entity(self.id, datetime.now()))

    def run(self):
        self.ready_socket()
        address = self.wait_for_probe()
        # try:
        self.run_loop(address)

    def run_loop(self, address):

        # loop part
        loop = asyncio.get_event_loop()

        listen_task = loop.create_datagram_endpoint(
            lambda: EchoServerProtocol(self),
            sock=self.server_socket
        )
        transport, protocol = loop.run_until_complete(listen_task)

        loop.create_task(self.log_forever())

        loop.create_task(self.serve_forever(address))

        # Running part
        print('loop is running')
        try:
            loop.run_until_complete(asyncio.sleep(self.time_of_sample_size))
        except KeyboardInterrupt:
            pass
        print()
        transport.close()
        self.shutdown()

    def wait_for_probe(self):
        self.server_socket.settimeout(self.socket_timeout)
        try:
            print("Server ready at: %s %s" % self.listening_address)
            request_and_address = self.server_socket.recvfrom(1024)

            address: Tuple[str, int] = request_and_address[1]
            print(f"Request from {address[0]}{address[1]}")
            print()
            return address
        except socket.timeout as e:
            print("Server timeout. Client didn't connect to server")
            print(e)
            return '192.168.0.144', 7071

    def ready_socket(self):
        try:
            # Assign IP address and port number to socket
            self.server_socket.bind(self.listening_address)
        except socket.error as error:
            exit("[ERROR] %s\n" % error)

    def log(self):
        packet_loss = self.calculate_packet_loss()

        print(
            f"{self.last_sent_packet} packets send | {self.last_received_packet} packets received"
            f" | packet loss: {packet_loss * 100}%",
            end='\r')

    async def log_forever(self):
        while True:
            self.log()
            await asyncio.sleep(self.log_interval)

    async def serve_forever(self, address):
        start_time = time.time()
        while True:
            self.send_packet(address)

            await asyncio.sleep(self.__interval - (time.time() - start_time) % self.__interval)

    def shutdown(self):
        self.server_socket.close()
        server_logger = Entity_Logger('server_send')
        server_logger.log(self.outgoing_packets)

        respond_logger = Entity_Logger('respond')
        respond_logger.log(self.incoming_packets)
        exit(1)

    def calculate_packet_loss(self):
        if self.last_sent_packet > 0 and self.last_received_packet > 0:
            pct_of_successful_packets = self.last_received_packet / self.last_sent_packet
            return 1 - pct_of_successful_packets
        return 0


class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        self.server = server
        self.transport = None

    def connection_made(self, transport):
        self.server.server_socket = transport
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        numbers = message.split('_')
        self.server.last_sent_packet = int(numbers[0])
        self.server.last_received_packet = int(numbers[1])

        self.server.incoming_packets.append(Packet_entity(message, datetime.now()))
