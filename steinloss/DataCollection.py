from class_patterns import Singleton
from TimeTable import TimeTable
from PacketTable import PacketTable
from Package import Package, ReceivePackage, SentPackage
from datetime import datetime



class DataCollection(metaclass=Singleton):
    def __init__(self) -> None:
        self.time_table = TimeTable()
        self.packet_table = PacketTable()

    def get_time_table(self):
        return self.time_table

    def get_packet_table(self):
        return self.packet_table

    def add(self, packet: Package):
        if type(packet) is SentPackage:
            self.packet_table[packet.id].sent_at = packet.time
        elif type(packet) is ReceivePackage:
            self.packet_table[packet.id].received_at = packet.time

            sent_timestamp = self.packet_table[packet.id].sent_at
            self.time_table[sent_timestamp].loss -= 1

        self.time_table[packet.time].add_packet(packet)

    def __contains__(self, item):
        if isinstance(item, Package):
            return item.id in self.packet_table
        elif isinstance(item, datetime):
            return item in self.time_table

    def __getitem__(self, key):
        if isinstance(key, datetime):
            return self.time_table[key]
        else:
            return self.packet_table[key]

    def __repr__(self):
        return f"{str(self.time_table)}\n{str(self.packet_table)}"

    def get_last_packages(self, number_of_packages: int):
        arr = []
        counter = number_of_packages
        i = iter(reversed(self.packet_table))

        while counter > 0:
            key = next(i)
            arr.append(self.packet_table[key])
            counter -= 1

        return arr

