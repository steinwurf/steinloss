import asyncio
import socket
from math import ceil

import pytest

from src.server import Server

kilobyte = 1024


class Test_server:

    @pytest.mark.parametrize(
        "speed, interval", [(kilobyte, 1), (2 * kilobyte, 0.5), (4 * kilobyte, 0.25)]
    )
    def test_two_kilobytes_should_set_interval_to_half(self, speed, interval):
        server = Server()
        server.speed = speed

        assert server.interval == interval

    def test_construct_server_with_five_kilobytes(self):
        five_kilobytes = 5120
        server = Server(five_kilobytes)

        assert server.interval == 0.2

    @pytest.mark.parametrize(
        "packets", [1, 2, 3, 4]
    )
    def test_send_packet_should_save_entry(self, mocker, packets, freezer):
        mocker.patch('socket.socket')
        server = Server()

        for _ in range(packets):
            server.send_packet(None)

        assert len(server.outgoing_packets) == packets

        id_string = server.outgoing_packets.pop().id
        assert int(id_string) == packets

    def test_wait_for_probe_should_return_address_of_probe(self, mocker):
        server = Server()
        fake_address = '0,1,2,3', 4321
        mocker.patch('socket.socket.recvfrom', return_value=[b"packet", fake_address])

        assert server.wait_for_probe() == fake_address

    def test_socket_bind_throws_exception_should__exit(self, mocker):
        server = Server()
        mocker.patch('socket.socket.bind', side_effect=socket.error())
        with pytest.raises(SystemExit, match=r"ERROR"):
            server.ready_socket()

    @pytest.mark.parametrize(
        "iterations", [1, 2, 3]
    )
    def test_send_packet_should_should_send_id_to_client(self, mocker, iterations):
        server = Server()
        probe_address = '1,3,3,7', 1001
        mocked_sendto = mocker.patch('socket.socket.sendto')
        for i in range(iterations):
            server.send_packet(probe_address)
            mocked_sendto.assert_called_with(('%d' % i).encode(), probe_address)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "speed, duration", [(4096, 0.2), (196608, 0.1)]
    )
    async def test_serve_forever_should_send_packets_according_to_speed(self, mocker, event_loop, speed, duration):
        mocked_sendto = mocker.patch('src.server.Server.send_packet')

        server = Server(speed=speed)

        event_loop.create_task(server.serve_forever('fake_adresse'))
        await asyncio.sleep(duration, loop=event_loop)

        assert mocked_sendto.call_count == ceil(speed * duration / kilobyte)

    # shutdown should log rest, and close socket
    def test_calculate_packet_loss_should_answer_in_pct_of_lost_packets(self, freezer):
        server = Server()
        server.last_sent_packet = 4
        server.last_received_packet = 3

        assert server.calculate_packet_loss() == 0.25


class FakeTime:
    def __init__(self):
        self.__time = 0

    def time(self):
        return self.__time

    def sleep(self, seconds):
        self.__time += seconds
