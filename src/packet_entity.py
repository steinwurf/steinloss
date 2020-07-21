class Packet_entity:
    def __init__(self, id, time):
        self.id = id
        self.time = time

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.time == other.time
        return False
