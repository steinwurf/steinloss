class Packet_entity:
    def __init__(self, packet_content, time):
        self.id = packet_content
        self.time = time

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.time == other.time
        return False
