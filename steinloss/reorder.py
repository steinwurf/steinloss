class Reorder:
    def __init__(self, window_size=3):
        self.lost = 0
        self.duplicate = 0
        # Sat to one, as the implementation would count packet number -2 and -1 as loss otherwise.
        self.reorder_window = self.reset_reorder_window(1)
        self.window_size = window_size
        self.sequence_number = -1

    @property
    def lower_bound(self):
        return self.sequence_number - self.window_size

    def consume_packet(self, incoming_seq_num: str):
        incoming_seq_num = int(incoming_seq_num)

        if self.lower_bound < incoming_seq_num < self.sequence_number:
            self.received_packet(incoming_seq_num)

        elif incoming_seq_num == self.sequence_number:  # duplicate
            self.duplicate += 1

        elif self.sequence_number < incoming_seq_num < self.sequence_number + self.window_size:
            self.handle_loss(incoming_seq_num)
            self.received_packet(incoming_seq_num)

            for n in range(self.sequence_number + 1, incoming_seq_num):
                self.handle_loss(incoming_seq_num - n)
                self.received_packet(incoming_seq_num - n, False)

        elif incoming_seq_num >= self.sequence_number + self.window_size:
            self.received_packet(incoming_seq_num)

            for n in range(self.lower_bound, self.sequence_number):
                self.handle_loss(n)
            self.reorder_window = self.reset_reorder_window(0)

            self.lost += self.loss_upto_new_bound(incoming_seq_num)

        self.sequence_number = max(incoming_seq_num, self.sequence_number)

    def reset_reorder_window(self, value):
        return [value] * self.window_size

    def loss_upto_new_bound(self, incoming_seq_num):
        return incoming_seq_num - self.window_size - self.sequence_number

    def handle_loss(self, incoming_seq_num):
        my_pos = incoming_seq_num % self.window_size
        print(my_pos)
        if self.reorder_window[my_pos] == 0:
            self.lost += 1

    def received_packet(self, incoming_seq_num, recived=True):
        my_pos = incoming_seq_num % self.window_size
        self.reorder_window[my_pos] = 1 if recived else 0

    def not_received_package(self, incoming_seq_num):
        my_pos = incoming_seq_num % self.window_size
        self.reorder_window[my_pos] = 0
