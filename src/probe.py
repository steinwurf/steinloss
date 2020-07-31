from socket import AF_INET, SOCK_DGRAM
import socket


class Probe:
    packet_size = 1024

    def __init__(self, server_address, address=('', 7071)):
        self.old_id = 0
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
        if self.is_packet_loss(packet):
            self.server_to_client_loss += 1
        print(
            f"\treceived message: {packet} | probe id: {self.id} |"
            f" server->probe loss: {self.server_to_client_loss}",
            end='\r')
        self.old_id = int(packet)
        self.respond_to_server(packet + f"_{self.id}")
        self.id += 1

    def respond_to_server(self, packet: str):
        self.sock.sendto(packet.encode(), self.server_address)

    def ping_server(self):
        self.respond_to_server('begin')

    def shutdown(self):
        pass

    def run_loop(self):
        while True:
            self.receive_packet()

    def is_packet_loss(self, packet):
        new_id = int(packet)

        return self.old_id + 1 == new_id
