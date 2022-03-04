from datetime import datetime

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


class PacketTable(dict):
    def __getitem__(self, key) -> PacketEntry:
        if key not in self.keys():
            self.__setitem__(key, PacketEntry())
        return super().__getitem__(key)

    def __repr__(self):
        return f"{type(self).__name__}: {super().__repr__()}"

    def __iter__(self):
        return super().__iter__()