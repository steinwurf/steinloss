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


class Server:
    packet_size = kilobyte

    def __init__(self, speed=kilobyte, listening_address=("127.0.0.1", 7070)):
        self.socket_timeout = 30  # seconds
        self.log_interval = 1
        self.test_is_running = False
        self.__logger = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listening_address = listening_address
        self.entries = []
        self.id = 0
        self.probe_address = None
        self.interval = 1
        self.speed = speed

    @property
    def speed(self):
        return 1 / self.interval * self.packet_size

    @speed.setter
    def speed(self, value):
        self.interval = self.packet_size / value

    @property
    def logger(self):
        if self.__logger is None:
            self.__logger = Entity_Logger('server_stats')
        return self.__logger

    @logger.setter
    def logger(self, value):
        self.__logger = value

    def send_packet(self, address):
        packet = "%d" % self.id
        self.server_socket.sendto(packet.encode(), address)

        self.id += 1
        self.save_entry()

    def save_entry(self):
        self.entries.append(Packet_entity(self.id, datetime.now()))

    # while loop
    # setup interval
    # def logger
    def run(self):
        self.ready_socket()

        address = self.wait_for_probe()

        self.serve_packets(address)

    def wait_for_probe(self):
        self.server_socket.settimeout(self.socket_timeout)
        try:
            print("Server ready at: %s %s" % self.listening_address)
            request_and_address = self.server_socket.recvfrom(1024)

            address: Tuple[str, int] = request_and_address[1]
            print("Request from %s %d" % address)
            return address
        except socket.timeout:
            print("Server timeout. Client didn't connect to server")
            self.shutdown()

    def ready_socket(self):
        try:
            # Assign IP address and port number to socket
            self.server_socket.bind(self.listening_address)
        except socket.error as error:
            exit("[ERROR] %s\n" % error)

    # def new_loop(self):

    def serve_packets(self, address):
        # https://docs.python.org/3/whatsnew/3.8.html : asyncio.run(main)
        try:
            self.test_is_running = True
            loop = asyncio.get_event_loop()
            loop.create_task(self.serve_forever(address))
            loop.create_task(self.log_forever())
            loop.run_forever()
        except KeyboardInterrupt:
            self.shutdown()

    def add_tasks_to_loop(self, loop, address):

        return loop

    def print_speed(self):
        hertz = ONE_SECOND / self.speed
        bytes_per_second = hertz * self.packet_size
        mb_per_second = bytes_per_second / 1000000
        print("%f Mb/s" % round(mb_per_second))

        pass

    async def log_forever(self):
        start_time = time.time()
        while True:
            self.logger.log(self.entries)
            self.entries = []
            await asyncio.sleep(self.log_interval - (time.time() - start_time) % self.log_interval)

    async def serve_forever(self, address):
        start_time = time.time()
        while True:
            self.send_packet(address)

            await asyncio.sleep(self.interval - (time.time() - start_time) % self.interval)

    def shutdown(self):
        pass
