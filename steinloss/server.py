import asyncio
import socket
import time
from datetime import datetime, timedelta
from typing import Tuple

from steinloss.Package import SentPackage, ReceivePackage, Package
from steinloss.utilities import log
from steinloss.DataCollection import DataCollection
ONE_SECOND = 1

kilobyte = 1024
megabyte = 1024 * kilobyte
gigabyte = 1048576 * kilobyte


class Server:
    packet_size = kilobyte

    def __init__(self, speed=megabyte, ip='0.0.0.0', port=7070,
                 runtime_of_test=ONE_SECOND * 60 * 30, batch_size=50):
        self.last_sent_packet = 0
        self.last_received_packet = 0
        self.time_of_sample_size = runtime_of_test
        self.socket_timeout = 60 * 5  # seconds
        self.log_interval = 1
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listening_address = (ip, port)
        self.id = 0
        self.speed = speed  # The speed in Bytes/s
        self.data_collection = DataCollection()

        self.batch_size = batch_size   # how much data to send in a batch in kilobytes
        self.__interval = self.batch_size / self.speed * 1024

        # making the port and host reusable:
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @property
    def interval(self):
        return self.__interval

    def run(self):
        self.ready_event_loop()
        self.ready_socket()

        try:
            address = self.wait_for_probe()
            self.run_loop(address)
        except Exception as e:
            log("Server timeout. Client didn't connect to server")
            log(e)
            raise e

    def ready_event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    def ready_socket(self):
        try:
            # Assign IP address and port number to socket
            self.server_socket.bind(self.listening_address)
        except socket.error as error:
            log("socket could not connect to host")
            self.shutdown()
            raise error

    def send_packet_batch(self, address):
        async def async_send_packet(address):
            packet = "%d" % self.id
            package = SentPackage(packet, self.timestamp())
            self.save_entry(package)
            self.id += 1
            self.server_socket.sendto(packet.encode(), address)

        loop = asyncio.get_event_loop()
        for _ in range(self.batch_size):
            loop.create_task(async_send_packet(address=address))

    def timestamp(self):
        return datetime.now()

    def wait_for_probe(self):
        self.server_socket.settimeout(self.socket_timeout)
        log("Server ready at: %-15s %s" % self.listening_address)
        log("Server ready at: %-15s %s" % (self.get_local_ip(), self.listening_address[1]))
        log("Waiting for a probe to ping")
        request_and_address = self.server_socket.recvfrom(1024)

        address: Tuple[str, int] = request_and_address[1]
        log(f"Request from {address[0]}{address[1]}")
        return address

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
        log('loop is running')

        try:
            loop.run_until_complete(asyncio.sleep(self.time_of_sample_size))
            log("Test is complete")
        except KeyboardInterrupt as error:
            log("test got interrupted")
            raise error
        finally:
            transport.close()
            self.shutdown()

    def save_entry(self, package: Package):
        self.data_collection.add(package)

    async def log_forever(self):
        while True:
            self.log()
            await asyncio.sleep(self.log_interval)

    def log(self):
        one_second_in_the_past = datetime.now() - timedelta(seconds=2)

        packet_loss = self.data_collection.get_package_loss_from_time(one_second_in_the_past)

        sent = self.data_collection.get_time_table()[one_second_in_the_past].sent
        received = self.data_collection.get_time_table()[one_second_in_the_past].received

        log(f"{sent} packets sent last second |"
            + f" {received} packets received last second ",
            " | package loss: {:.2f}".format(packet_loss * 100),
            end='\r')

    async def serve_forever(self, address):
        start_time = 0
        end_time = 0
        while True:
            self.send_packet_batch(address)
            end_time = time.perf_counter()
            await asyncio.sleep(self.__interval - (end_time - start_time))
            start_time = time.perf_counter()

    def shutdown(self):
        self.server_socket.close()
        tasks = asyncio.Task.all_tasks()
        for task in tasks:
            task.cancel()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip


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
        sent_packet = numbers[0]
        received_packet = numbers[1]

        package = ReceivePackage(sent_packet, received_packet, datetime.now())
        self.server.data_collection.add(package)
