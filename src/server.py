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

    def __init__(self, speed=megabyte, listening_address=('0.0.0.0', 7070),
                 time_of_sample_size=ONE_SECOND * 60 * 4):
        self.time_of_sample_size = time_of_sample_size
        self.socket_timeout = 10  # seconds
        self.log_interval = 1
        self.__logger = None
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
    def logger(self):
        if self.__logger is None:
            self.__logger = Entity_Logger('server_stats')
        return self.__logger

    @property
    def interval(self):
        return self.__interval

    @logger.setter
    def logger(self, value):
        self.__logger = value

    def send_packet(self, address):
        packet = "%d" % self.id
        self.server_socket.sendto(packet.encode(), address)

        self.id += 1
        self.save_entry()

    def save_entry(self):
        self.outgoing_packets.append(Packet_entity(self.id, datetime.now()))

    # while loop
    # setup interval
    # def logger
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

        ## running part
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

    def test_front_end_log(self):
        outgoing_packets = len(self.outgoing_packets)
        incoming_packets = len(self.incoming_packets)
        packet_loss = self.calculate_packet_loss()

        print(
            f"{outgoing_packets} packets send | {incoming_packets} packets received | packet loss: {packet_loss * 100}%",
            end='\r')

    async def log_forever(self):
        while True:
            self.test_front_end_log()
            await asyncio.sleep(self.log_interval)

    async def serve_forever(self, address):
        start_time = time.time()
        while True:
            self.send_packet(address)

            await asyncio.sleep(self.__interval - (time.time() - start_time) % self.__interval)

    def shutdown(self):
        self.server_socket.close()
        self.logger.log(self.outgoing_packets)
        self.logger.log(self.incoming_packets)
        exit(1)

    def calculate_packet_loss(self):
        if not self.incoming_packets or not self.outgoing_packets:
            return 1 - len(self.incoming_packets) / len(self.outgoing_packets)


class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        self.server = server
        self.transport = None

    def connection_made(self, transport):
        self.server.server_socket = transport
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        self.server.incoming_packets.append(Packet_entity(message, datetime.now()))
