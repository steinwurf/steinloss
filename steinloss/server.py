import asyncio
import socket
import time
from datetime import datetime, timedelta
from typing import Tuple

from steinloss import log
from steinloss.Data_Presenter import Data_Presenter
from steinloss.package import SentPackage, ReceivePackage, Package

ONE_SECOND = 1

kilobyte = 1024
megabyte = 1024 * kilobyte
gigabyte = 1048576 * kilobyte


class Server:
    packet_size = kilobyte

    def __init__(self, speed=megabyte, ip='0.0.0.0', port=7070,
                 runtime_of_test=ONE_SECOND * 60 * 30):
        self.last_sent_packet = 0
        self.last_received_packet = 0
        self.time_of_sample_size = runtime_of_test
        self.socket_timeout = 60 * 5  # seconds
        self.log_interval = 1
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listening_address = (ip, port)
        self.id = 0
        self.__interval = 1
        self.speed = speed
        self.data_presenter = Data_Presenter.get_instance()

    @property
    def speed(self):
        return 1 / self.__interval * self.packet_size

    @speed.setter
    def speed(self, value):
        self.__interval = self.packet_size / value

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

    def send_packet(self, address):
        packet = "%d" % self.id

        package = SentPackage(packet, self.timestamp())
        self.save_entry(package)
        self.id += 1
        self.server_socket.sendto(packet.encode(), address)

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

        # loop.create_task(self.log_forever())
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
        self.data_presenter.append(package)

    async def log_forever(self):
        while True:
            self.log()
            await asyncio.sleep(self.log_interval)

    def log(self):
        one_second_in_the_past = datetime.now() - timedelta(seconds=2)

        packet_loss = self.calculate_packet_loss_in_pct(one_second_in_the_past)

        sent = self.data_presenter.get_time_table()[one_second_in_the_past].sent
        received = self.data_presenter.get_time_table()[one_second_in_the_past].received

        log(f"{sent} packets sent last second |"
            + f" {received} packets received last second ",
            " | package loss: {:.2f}".format(packet_loss * 100),
            end='\r')

    async def serve_forever(self, address):
        start_time = time.time()
        while True:
            self.send_packet(address)

            await asyncio.sleep(self.__interval - (time.time() - start_time) % self.__interval)

    def calculate_packet_loss_in_pct(self, timestamp: datetime):
        time_entry = self.data_presenter.get_time_table()[timestamp]
        packages_sent = time_entry.sent
        packages_recv = time_entry.received

        if packages_sent == 0 or packages_recv == 0:
            return 0
        else:
            return 1 - packages_recv / packages_sent

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
        self.server.data_presenter.append(package)
