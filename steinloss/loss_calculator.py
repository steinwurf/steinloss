from datetime import datetime

from steinloss.package import Package, ReceivePackage, SentPackage


class TimeEntry:
    def __init__(self):
        self.loss = 0
        self.sent = 0
        self.received = 0

    def add_packet(self, packet):
        if type(packet) is SentPackage:
            self.sent += 1
            self.loss += 1
        elif type(packet) is ReceivePackage:
            self.received += 1

    def __repr__(self):
        return f"{type(self).__name__}: loss:{self.loss} - SentPackage:{self.sent} received:{self.received}"


class TimeTable:
    def __init__(self):
        self.dict = dict()

    def __getitem__(self, key) -> TimeEntry:
        if isinstance(key, datetime):
            time_key = self.convert_time_to_key(key)
        else:
            time_key = key
        if time_key not in self.dict.keys():
            self.dict[time_key] = TimeEntry()
        return self.dict[time_key]

    @staticmethod
    def convert_time_to_key(packet_time: datetime):
        return packet_time.strftime("%H:%M:%S")

    def __repr__(self):
        return f"{type(self).__name__}: {str(self.dict)}"

    def __iter__(self):
        return iter(self.dict)


class PacketEntry:
    sent_at: datetime
    received_at: datetime

    def __init__(self):
        self.sent_at = None
        self.received_at = None

    def is_sent(self):
        return self.sent_at is not None

    def is_received(self):
        return self.received_at is not None

    def __repr__(self):
        return f"{type(self).__name__}: sent:{self.sent_at} → recv:{self.received_at}"


class packet_table(dict):
    def __getitem__(self, key) -> PacketEntry:
        if key not in self.keys():
            self.__setitem__(key, PacketEntry())
        return super().__getitem__(key)

    def __repr__(self):
        return f"{type(self).__name__}: {super().__repr__()}"

    def __iter__(self):
        return super().__iter__()


class Loss_Calculator:
    def __init__(self):
        self.time_table = TimeTable()
        self.packet_table = packet_table()

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

    def get_last_packages(self, number_of_packages: int) -> [PacketEntry]:
        arr = []
        counter = number_of_packages
        i = iter(reversed(self.packet_table))

        while counter > 0:
            key = next(i)
            arr.append(self.packet_table[key])
            counter -= 1

        return arr
