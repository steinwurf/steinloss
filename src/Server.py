import csv
import threading
import socket
import time

from src.entity_logger import Entity_Logger

DECREASE_RATIO = 0.95
ONE_SECOND = 1

log = Entity_Logger()


class PacketSenderThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(PacketSenderThread, self).__init__()
        self.target = target
        self.name = name


class PacketLoggerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(PacketLoggerThread, self).__init__()
        self.target = target
        self.name = name
        return


class Server(object):
    packet_size_in_bytes = 1024

    def __init__(self, x):
        self.id = 0
        self.interval = 1
        self.set_interval(x)

    def serve_packets(self):
        listening_address = ("127.0.0.1", 7070)
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Assign IP address and port number to socket
        server_socket.bind(listening_address)
        with open('../data/server_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["packets", "timestamp"])
        print("Server ready at: %s %s" % listening_address)

        request_and_address = server_socket.recvfrom(1024)
        address = request_and_address[1]
        print("Request from %s %d" % address)

        self.post_results()
        while True:
            packet = "%d" % self.id
            server_socket.sendto(packet.encode(), address)
            self.id += 1
            self.wait_interval()

    def set_interval(self, x):
        self.interval = x

    def get_interval(self):
        return self.interval

    def wait_interval(self):
        self.print_speed()
        if self.interval < 0.001:
            print("packets: ", self.id.numerator)
            exit()
        time.sleep(self.interval)
        self.set_interval(self.interval * DECREASE_RATIO)
        self.set_interval(self.interval * DECREASE_RATIO)
        pass

    def print_speed(self):
        hertz = ONE_SECOND / self.interval
        bytes_per_second = hertz * self.packet_size_in_bytes
        mb_per_second = bytes_per_second / 1000000
        print("%f Mb/s" % round(mb_per_second))

        pass

    def post_results(self):
        threading.Timer(1.0, self.post_results).start()
        with open('../data/server_stats.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.id, time.strftime("%H:%M:%S", time.localtime())])
