class Reorder:
    def __init__(self, window_size=3):
        self.lost = 0
        self.duplicate = 0
        # Sat to one, as the implementation would count packet number -2 and -1 as loss otherwise.
        self.reorder_window = [1] * window_size
        self.window_size = window_size
        self.max_sequence_number = -1

    @property
    def lower_bound(self):
        return self.max_sequence_number - self.window_size

    def consume_packet(self, incoming_seq_num: str):
        incoming_seq_num = int(incoming_seq_num)

        if self.lower_bound < incoming_seq_num < self.max_sequence_number:
            self.recived_packet(incoming_seq_num)

        if incoming_seq_num == self.max_sequence_number - 0:  # duplicate
            self.duplicate += 1

        # if self.max_sequence_number < incoming_seq_num < self.max_sequence_number + 2:
        #     self.handle_loss(incoming_seq_num)
        #     self.recived_packet(incoming_seq_num)
        #
        #     for n in range(self.max_sequence_number + 1, incoming_seq_num):
        #         self.handle_loss(incoming_seq_num - n)
        #         self.not_received_package(incoming_seq_num - n)

        if incoming_seq_num == self.max_sequence_number + 1:
            self.handle_loss(incoming_seq_num)
            self.recived_packet(incoming_seq_num)

        if incoming_seq_num == self.max_sequence_number + 2:
            self.handle_loss(incoming_seq_num)
            self.recived_packet(incoming_seq_num)

            for n in range(self.max_sequence_number + 1, incoming_seq_num):
                self.handle_loss(incoming_seq_num - n)
                self.not_received_package(incoming_seq_num - n)

        if incoming_seq_num > self.max_sequence_number + 2:
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
            old_lower_bound = self.max_sequence_number - 2
            old_upper_bound = self.max_sequence_number + 1  # non inclusive

            new_lower_bound = incoming_seq_num - 2
            new_upper_bound = incoming_seq_num + 1  # non inclusive
            for bit in self.get_bits(old_lower_bound, old_upper_bound):  # get bit
                if self.reorder_window[bit] == 0:
                    self.lost += 1
            self.lost += new_lower_bound - old_upper_bound

            self.reorder_window = [0, 0, 0]
            self.recived_packet(incoming_seq_num)

            # tæl packet loss fra seneste sequence number til packet number minus 2
            # sæt array til 0
            pass

        self.max_sequence_number = max(incoming_seq_num, self.max_sequence_number)

    def handle_loss(self, incoming_seq_num):
        my_pos = incoming_seq_num % self.window_size
        print(my_pos)
        if self.reorder_window[my_pos] == 0:
            self.lost += 1

    def recived_packet(self, incoming_seq_num):
        my_pos = incoming_seq_num % self.window_size
        self.reorder_window[my_pos] = 1

    def get_bits(self, lower_bound, upper_bound):

        difference = upper_bound - lower_bound
        if difference >= self.window_size:
            range_of_all_positions = range(self.window_size)
            return range_of_all_positions

        arr = []
        for n in range(lower_bound, upper_bound):
            position = n % self.window_size
            arr.append(position)
        return arr

    def not_received_package(self, incoming_seq_num):
        my_pos = incoming_seq_num % self.window_size
        self.reorder_window[my_pos] = 0
