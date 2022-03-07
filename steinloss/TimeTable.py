from steinloss.Package import Package, ReceivePackage, SentPackage
from datetime import datetime


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
