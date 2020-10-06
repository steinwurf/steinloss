from src.packet_entity import Packet_entity


class Loss_Calculator:
    packet_table = dict()

    def add(self, packet: Packet_entity):
        self.packet_table[packet.id] = packet

    def __getitem__(self, item):
        return self.packet_table[item]
