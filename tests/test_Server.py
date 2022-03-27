from steinloss.server import Server
from steinloss.DataCollection import DataCollection
import pytest
from datetime import datetime

KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE


class TestServer:
    @pytest.mark.parametrize(
        "speed, batchsize, interval", [(KILOBYTE, 1, 1), (4 * MEGABYTE, 100, 0.0244140625), (8 * MEGABYTE,
        50, 0.006103515625)]
    )
    def test_two_kilobytes_should_set_interval_to_half(self, speed, batchsize, interval):
        server = Server(speed=speed, batch_size=batchsize)
        assert server.interval == interval

    def test_wait_for_probe_should_return_address_of_probe(self, mocker):
        server = Server()
        fake_address = '0,1,2,3', 4321
        mocker.patch('socket.socket.recvfrom', return_value=[b"package", fake_address])

        assert server.wait_for_probe() == fake_address
        