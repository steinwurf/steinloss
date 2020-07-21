import csv
import threading
import socket
import time

from src.packet_entity import Packet_entity

ONE_SECOND = 1


class Server:
    kilobyte = 1024
    megabyte = 1024 * kilobyte

    packet_size = kilobyte

    def __init__(self, x=kilobyte):
        self.Entries = []
        self.id = 0
        self.interval = 1
        self.speed = x

    @property
    def speed(self):
        return 1 / self.interval * self.packet_size

    @speed.setter
    def speed(self, value):
        self.interval = self.packet_size / value

    def send_packet(self):
        self.save_entry()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        adresse = '0.0.0.0', 7070
        server_socket.sendto('1'.encode(), adresse)

    def save_entry(self):
        self.Entries.append(Packet_entity(self.id, time.time()))
        self.id += 1

    def send_for_n_seconds(self, seconds):
        start_timestamp = time.time()
        while time.time() < start_timestamp + seconds:
            self.send_packet()
            time.sleep(self.interval)

    # while loop
    # setup interval
    # def logger
    def serve_packets(self):
        listening_address = ("127.0.0.1", 7070)
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Assign IP address and port number to socket
        server_socket.bind(listening_address)
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

    def wait_interval(self):
        print(self.interval)
        time.sleep(self.interval)

    def print_speed(self):
        hertz = ONE_SECOND / self.speed
        bytes_per_second = hertz * self.packet_size
        mb_per_second = bytes_per_second / 1000000
        print("%f Mb/s" % round(mb_per_second))

        pass

    def post_results(self):
        threading.Timer(1.0, self.post_results).start()
        with open('../data/server_stats.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.id, time.strftime("%H:%M:%S", time.localtime())])
