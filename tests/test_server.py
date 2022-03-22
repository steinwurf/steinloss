""" import asyncio
import pytest

from datetime import datetime
from steinloss.DataCollection import DataCollection
from steinloss.Package import SentPackage, ReceivePackage
from steinloss.server import Server

kilobyte = 1024


class TestServer:

    def teardown_method(self):
        DataCollection.clear()

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

    @pytest.mark.parametrize("packets", [1, 2, 3, 4])
    def test_send_packet_should_save_entry(self, mocker, packets):
        mocker.patch('socket.socket')
        time = datetime.now()
        mocker.patch('steinloss.server.Server.timestamp', return_value=time)
        server = Server()

        for i in range(packets):
            server.send_packet('ip_address')

        assert server.data_collection.get_time_table()[time].sent == packets

    def test_wait_for_probe_should_return_address_of_probe(self, mocker):
        server = Server()
        fake_address = '0,1,2,3', 4321
        mocker.patch('socket.socket.recvfrom', return_value=[b"package", fake_address])

        assert server.wait_for_probe() == fake_address

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
        "speed, duration, packages", [(4096, 0.24, 1), (8192, 0.24, 2)]
    )
    async def test_serve_forever_should_send_packets_according_to_speed(
            self, mocker, event_loop, speed, duration, packages):
        mocked_sendto = mocker.patch('steinloss.server.Server.send_packet')

        server = Server(speed=speed)

        event_loop.create_task(server.serve_forever('fake_address'))
        await asyncio.sleep(duration, loop=event_loop)

        assert mocked_sendto.call_count == packages


class FakeTime:
    def __init__(self):
        self.__time = 0

    def time(self):
        return self.__time

    def sleep(self, seconds):
        self.__time += seconds
 """