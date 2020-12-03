from socket import AF_INET, SOCK_DGRAM
import socket


class Probe:
    packet_size = 1024

    def __init__(self, server_address, address=('', 7071)):
        self.window_size = 3
        self.lost = 0
        self.duplicate = 0
        self.reorder = 0
        self.sequence_number = None
        self.server_to_client_loss = 0
        self.suspect = [0] * 5
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

        self.sequence_number = int(packet)

        self.respond_to_server(packet + f"_{self.id}")
        self.id += 1

        if self.lost == 0 or self.sequence_number == 0:
            lost_pct = 0
        else:
            lost_pct = self.lost / self.sequence_number
        print(
            f"received message: {self.sequence_number} | probe id: {self.id} | ",
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

    def consume_packet(self, packet):
        full_window = self.window_size + 2
        packet = int(packet)
        pos = packet % full_window

        if self.sequence_number is None:
            self.sequence_number = packet - 1

        if packet > self.sequence_number:  # det er en ny pakke
            # Move window forward from 2 being middle, to 3 being middle
            # [0,1,2,3,4]
            # [0,0,0,1,1]

            # [5,1,2,3,4]
            # [1,0,0,0,1]

            # kun kig på det her, hvis vi er hoppet two tal
            two_up = (pos - 2) % 5
            if self.suspect[two_up] == 1:
                self.lost += 1
            self.suspect[two_up] = 1

            if packet > (self.sequence_number + 1):
                one_up = (pos - 1) % 5
                if self.suspect[one_up] == 1:
                    self.lost += 1
                self.suspect[one_up] = 1

            # set my pos to found
            self.suspect[pos] = 0  # no loss
            pass

        if packet == self.sequence_number:
            # duplication
            pass
        if packet < self.sequence_number:
            # is it in reordering window?
            if packet < self.sequence_number - self.window_size:
                # it is an old package.
                # The loss of this package is already counted
                pass
            else:
                # in reordering window
                # Tell that one of the packages in the reordering window is found
                self.suspect[pos] = 0
                # update my pos to found
                pass

        self.sequence_number = max(packet, self.sequence_number)
