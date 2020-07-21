import time
import pytest
from src.Server import Server
from src.packet_entity import Packet_entity


def test_two_kilobytes_should_set_interval_to_half():
    two_kilobytes = 2048
    server = Server()
    server.speed = two_kilobytes

    assert server.interval == 0.5


def test_four_kilobytes_should_set_interval_to_quarter():
    four_kilobytes = 4096
    server = Server()
    server.speed = four_kilobytes

    assert server.interval == 0.25


def test_construct_server_with_five_kilobytes():
    five_kilobytes = 5120
    server = Server(five_kilobytes)

    assert server.interval == 0.2


@pytest.mark.parametrize(
    "speed,packets_send", [(1024, 1), (2048, 2), (4096, 4)]
)
def test_send_packets_at_n_kilobytes_should_send_n_times(mocker, speed, packets_send):
    fake_time = FakeTime()
    time.time = fake_time.time
    time.sleep = fake_time.sleep

    mocked_run = mocker.patch('src.Server.Server.send_packet')

    server = Server(speed)
    server.send_for_n_seconds(1)

    assert mocked_run.call_count == packets_send


@pytest.mark.parametrize(
    "index", [0, 1, 2, 3, 4]
)
def test_send_packet_should_save_entry(mocker, index):
    timestamp = time.time()
    mocker.patch('time.time', return_value=timestamp)
    server = Server()
    for _ in range(index + 1):
        server.send_packet()

    actual = Packet_entity(index, timestamp)
    assert server.Entries[index].id == actual.id, "id"
    assert server.Entries[index].time == actual.time, "timestamp"


def test_send_packet_should_call_socket_sendto(mocker):
    mocked_socket = mocker.patch('socket.socket.sendto', return_value='')
    server = Server()
    server.send_packet()

    assert mocked_socket.call_count == 1


class FakeTime:
    def __init__(self):
        self.__time = time.time()

    def time(self):
        return self.__time

    def sleep(self, seconds):
        self.__time += seconds
