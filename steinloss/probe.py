import socket
from socket import AF_INET, SOCK_DGRAM

from steinloss.reorder import Reorder


def get_bits(old_upper_bound, old_upper_bound1):
    pass


class Probe:
    packet_size = 1024

    def __init__(self, server_address, address=('', 7071)):
        self.window_size = 3
        self.lost = 0
        self.duplicate = 0
        self.reorder = 0
        self.max_sequence_number = 0
        self.server_to_client_loss = 0
        self.reorder_window = [1] * self.window_size
        self.server_address = server_address
        self.address = address
        self.id = 0
        self.sock = socket.socket(SOCK_DGRAM, AF_INET)
        self.sock.bind(self.address)
        self.reorder = Reorder()

    def main(self):
        self.ping_server()
        self.run_loop()

    def run(self):
        try:
            self.respond_to_server('go')
            self.run_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def receive_packet(self):
        packet = self.sock.recv(self.packet_size).decode()

        self.consume_packet(packet)

        self.max_sequence_number = int(packet)

        self.respond_to_server(packet + f"_{self.id}")
        self.id += 1

        if self.lost == 0 or self.max_sequence_number == 0:
            lost_pct = 0
        else:
            lost_pct = self.lost / self.max_sequence_number
        print(
            f"received message: {self.max_sequence_number} | probe id: {self.id} | ",
            "server->probe loss: {:.2f}%".format(lost_pct * 100),
            end='\r')

    def respond_to_server(self, packet: str):
        self.sock.sendto(packet.encode(), self.server_address)

    def ping_server(self):
        self.respond_to_server('begin')

    def shutdown(self):
        pass

    def run_loop(self):
        while True:
            self.receive_packet()

    def consume_packet(self, incomming_seq_num):
        self.reorder.consume_packet(incomming_seq_num)


class ReorderWindow:
    def __init__(self, window_size):
        self.loss = 0
        self.duplicate = 0

    def __get_bits(self) -> [bool]:
        pass

    def consume_packet(self, pakke):
        return

    @property
    def get_loss(self):
        return self.loss
