import socket
from socket import AF_INET, SOCK_DGRAM


class Probe:
    packet_size = 1024

    def __init__(self, server_address, address=('', 7071)):
        self.window_size = 3
        self.lost = 0
        self.duplicate = 0
        self.reorder = 0
        self.sequence_number = 0
        self.server_to_client_loss = 0
        self.suspect = [1] * self.window_size
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
        window_size = 3
        packet = int(packet)

        # >>>>> 0
        # [0,1,2]
        # [1,1,1]
        # hvis packet - 2 mod 3 er 0 så har vi packet loss
        # 0 - 2 mod 3 = 1
        # [0,1,2]
        # [1,0,1]
        # hvis packet - 2 mod 3 er 0 så har vi packet loss
        # 1 - 2 mod 3 = 2
        # >>>>> 1
        # [0,1,2]
        # [1,0,1]

        # [0,1,2]
        # [1,1,1]

        # >>>>> 2
        # [3,1,2]
        # [0,1,0]

        # [3,4,2]
        # [0,0,1]

        # så hvis vi bare får det næste tal,

        if packet < self.sequence_number - 2:
            # Er allerede talt som packet loss
            # ikke gør noget
            pass
        # same
        if packet == self.sequence_number - 2:
            # indenfor reorder
            # vend plads til 1
            my_pos = packet % window_size
            self.suspect[my_pos] = 1
            pass
        if packet == self.sequence_number - 1:
            # indenfor reorder
            # vend plads til 1
            my_pos = packet % window_size
            self.suspect[my_pos] = 1
            pass
        if packet == self.sequence_number - 0:  # duplicate
            # duplication ?
            # ikke gør noget
            pass
        if packet == self.sequence_number + 1:
            # hvis det tal jeg skal til at sætte til 1, er 0. Så packet loss
            # har ikke fået 2
            # [3,4,2]
            # [1,1,0]
            # får 5

            # [3,4,5]
            # [1,1,1]
            # +1 loss
            my_pos = packet % window_size
            if self.suspect[my_pos] == 0:
                self.lost += 1
            self.suspect[my_pos] = 1

        if packet == self.sequence_number + 2:
            # hvis det tal jeg skal til at sætte til 1, er 0. Så packet loss
            # hvis det tallet bag min position          er 0. Så packet loss

            # har ikke fået 2
            # [3,4,2]
            # [1,1,0]
            # får 6

            # [6,4,5]
            # [1,1,0]
            # +1 loss
            # venter stadig på at få 5
            my_pos = packet % window_size
            if self.suspect[my_pos] == 0:
                self.lost += 1
            self.suspect[my_pos] = 1

            behind_me_pos = (packet - 1) % window_size
            if self.suspect[behind_me_pos] == 0:
                self.lost += 1
            self.suspect[behind_me_pos] = 0

            pass

        if packet > self.sequence_number + 2:
            packet_out_of_reorder_window = packet - self.window_size
            loss_we_know = packet_out_of_reorder_window - self.sequence_number
            self.lost += loss_we_know

            self.suspect = [0, 0, 0]
            my_pos = packet % window_size
            self.suspect[my_pos] = 1

            # tæl packet loss fra seneste sequence number til packet number minus 2
            # sæt array til 0
            pass

        self.sequence_number = max(packet, self.sequence_number)
