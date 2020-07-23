import asyncio
import socket
from datetime import datetime
from math import ceil

import pytest
from src.Server import Server
from src.packet_entity import Packet_entity

kilobyte = 1024


@pytest.mark.parametrize(
    "speed, interval", [(kilobyte, 1), (2 * kilobyte, 0.5), (4 * kilobyte, 0.25)]
)
def test_two_kilobytes_should_set_interval_to_half(speed, interval):
    server = Server()
    server.speed = speed

    assert server.interval == interval


def test_construct_server_with_five_kilobytes():
    five_kilobytes = 5120
    server = Server(five_kilobytes)

    assert server.interval == 0.2


@pytest.mark.parametrize(
    "speed,packets_send", [(1024, 1), (2048, 2), (4096, 4)]
)
def test_send_packets_at_n_kilobytes_should_send_n_times(mocker, speed, packets_send):
    fake_time = FakeTime()
    mocker.patch('time.time', new=fake_time.time)
    mocker.patch('time.sleep', new=fake_time.sleep)
    mocked_run = mocker.patch('src.Server.Server.send_packet')

    server = Server(speed)
    server.send_for_n_seconds(1)

    assert mocked_run.call_count == packets_send


@pytest.mark.parametrize(
    "index, packet_id", [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
)
def test_send_packet_should_save_entry(mocker, index, packet_id, freezer):
    mocker.patch('socket.socket.sendto')

    server = Server()
    for _ in range(index + 1):
        server.send_packet(None)

    expected = Packet_entity(packet_id, datetime.now())
    assert server.entries[index].id == expected.id, "id"
    assert server.entries[index].time == expected.time, "timestamp"


def test_send_packet_should_call_socket_sendto(mocker):
    mocked_socket = mocker.patch('socket.socket.sendto')
    server = Server()
    server.send_packet('address placeholder')

    assert mocked_socket.call_count == 1


def test_run_should_respond_to_probe(mocker):
    server = Server()

    fake_address = ('0,1,2,3', 4321)
    mocked_server_packets = mocker.patch('src.Server.Server.serve_packets')
    mocker.patch('socket.socket.recvfrom', return_value=['packet', fake_address])

    server.run()
    mocked_server_packets.assert_called_once_with(fake_address)  # assert


def test_socket_bind_throws_exception_should__exit(mocker):
    server = Server()
    mocker.patch('socket.socket.bind', side_effect=socket.error())
    with pytest.raises(SystemExit, match=r"ERROR"):
        server.ready_socket()


@pytest.mark.parametrize(
    "iterations", [1, 2, 3]
)
def test_send_packet_should_should_send_id_to_client(mocker, iterations):
    server = Server()
    probe_address = '1,3,3,7', 1001
    mocked_sendto = mocker.patch('socket.socket.sendto')
    for i in range(iterations):
        server.send_packet(probe_address)
        mocked_sendto.assert_called_with(('%d' % i).encode(), probe_address)


@pytest.mark.asyncio
async def test_log_forever_should_log_twice_after_two_second(mocker, event_loop):
    server = Server()
    server.log_interval = 0.01

    mocked_log_method = mocker.patch.object(server.logger, 'log')
    event_loop.create_task(server.log_forever())
    await asyncio.sleep(0.1, loop=event_loop)

    assert mocked_log_method.call_count == 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "speed, duration", [(4096, 0.2), (196608, 0.1)]
)
async def test_serve_forever_should_send_packets_according_to_speed(mocker, event_loop, speed, duration):
    mocked_sendto = mocker.patch('socket.socket.sendto')

    server = Server(speed=speed)

    event_loop.create_task(server.serve_forever('fake_adresse'))
    await asyncio.sleep(duration, loop=event_loop)

    assert mocked_sendto.call_count == ceil(speed * duration / kilobyte)


class FakeTime:
    def __init__(self):
        self.__time = 0

    def time(self):
        return self.__time

    def sleep(self, seconds):
        self.__time += seconds
