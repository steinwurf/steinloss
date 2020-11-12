from datetime import datetime


class Packet_entity:
    def __init__(self, packet_content, time=datetime.now()):
        self.id = packet_content
        self.time = time

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"id: {self.id} | time:  {self.time.strftime('%H:%M:%S')}"


class sent_package(Packet_entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class receive_package(Packet_entity):
    def __init__(self, sent_id, recv_id, *kwargs):
        self.recv_id = recv_id
        super().__init__(sent_id, *kwargs)

    def __repr__(self):
        return f"id:{self.id} recv:{self.recv_id} time:{self.time}"
