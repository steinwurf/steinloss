import socket
from socket import AF_INET, SOCK_DGRAM


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
        window_size = 3
        incomming_seq_num = int(incomming_seq_num)

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

        if incomming_seq_num < self.max_sequence_number - 2:  # udenfor window
            # Er allerede talt som packet loss
            # ikke gør noget
            pass
        # same
        if incomming_seq_num == self.max_sequence_number - 2:
            # indenfor reorder
            # vend plads til 1
            my_pos = incomming_seq_num % window_size
            self.reorder_window[my_pos] = 1
            pass
        if incomming_seq_num == self.max_sequence_number - 1:
            # indenfor reorder
            # vend plads til 1
            my_pos = incomming_seq_num % window_size
            self.reorder_window[my_pos] = 1
            pass
        if incomming_seq_num == self.max_sequence_number - 0:  # duplicate
            # duplication ?
            # ikke gør noget
            pass
        if incomming_seq_num == self.max_sequence_number + 1:
            # hvis det tal jeg skal til at sætte til 1, er 0. Så packet loss
            # har ikke fået 2
            # [3,4,2]
            # [1,1,0]
            # får 5

            # [3,4,5]
            # [1,1,1]
            # +1 loss
            my_pos = incomming_seq_num % window_size
            if self.reorder_window[my_pos] == 0:
                self.lost += 1
            self.reorder_window[my_pos] = 1

        if incomming_seq_num == self.max_sequence_number + 2:
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
            my_pos = incomming_seq_num % window_size
            if self.reorder_window[my_pos] == 0:
                self.lost += 1
            self.reorder_window[my_pos] = 1

            behind_me_pos = (incomming_seq_num - 1) % window_size
            if self.reorder_window[behind_me_pos] == 0:
                self.lost += 1
            self.reorder_window[behind_me_pos] = 0

        if incomming_seq_num > self.max_sequence_number + 2:
            # husk at tælle gamle fået pakker

            # har ikke fået 2
            # [3,4,2]
            # [1,1,0]
            # max seq = 5

            # [2,3,4][5,6,7]
            #

            # får 7
            # new_lower_bound = 5
            # [6,7,5]
            # [0,1,0]
            # old_lower_bound = self.max_sequence_number - 2
            # old_upper_bound = self.max_sequence_number + 1  # non inclusive
            #
            # new_lower_bound = incomming_seq_num - 2
            # new_upper_bound = incomming_seq_num + 1  # non inclusive
            # for bit in get_bits(old_upper_bound, old_upper_bound):  # get bit
            #     if self.reorder_window[bit] == 0:
            #         self.lost += 1
            # self.lost += new_lower_bound - old_upper_bound

            self.reorder_window = [0, 0, 0]
            my_pos = incomming_seq_num % window_size
            self.reorder_window[my_pos] = 1

            # tæl packet loss fra seneste sequence number til packet number minus 2
            # sæt array til 0
            pass

        self.max_sequence_number = max(incomming_seq_num, self.max_sequence_number)


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
