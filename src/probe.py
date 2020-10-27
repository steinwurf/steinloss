from socket import AF_INET, SOCK_DGRAM
import socket


class Probe:
    packet_size = 1024

    def __init__(self, server_address, address=('', 7071)):
        self.reordering_window = 3
        self.lost = 0
        self.duplicate = 0
        self.reorder = 0
        self.id_on_last_received_packet = None
        self.server_to_client_loss = 0
        self.server_address = server_address
        self.address = address
        self.id = 0
        self.sock = socket.socket(SOCK_DGRAM, AF_INET)
        self.sock.bind(self.address)

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

        self.id_on_last_received_packet = int(packet)

        self.respond_to_server(packet + f"_{self.id}")
        self.id += 1

        if self.lost == 0 or self.id_on_last_received_packet == 0:
            lost_pct = 0
        else:
            lost_pct = self.lost / self.id_on_last_received_packet
        print(
            f"received message: {self.id_on_last_received_packet} | probe id: {self.id} |" +
            " server->probe loss: {:.2f}%".format(lost_pct * 100),
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

    def consume_packet(self, packet):
        sequence_number = int(packet)
        if self.id_on_last_received_packet:
            if sequence_number > self.id_on_last_received_packet:
                lost = sequence_number - self.id_on_last_received_packet - 1
                self.lost += lost
            elif sequence_number < self.id_on_last_received_packet:
                if sequence_number > self.id_on_last_received_packet - self.reordering_window:
                    self.lost -= 1
        else:
            self.id_on_last_received_packet = sequence_number

        self.id_on_last_received_packet = max(sequence_number, self.id_on_last_received_packet)
