import socket
import pytest

from src.probe import Probe


@pytest.mark.usefixtures('socket')
class Test_probe:

    @pytest.fixture(autouse=True)
    def mock_env_socket(mocker, monkeypatch):
        monkeypatch.setattr(socket, 'socket', return_value=mocker.patch('socket.socket'))

    def setup_method(self):
        self.probe = Probe(('fake_address', 1337))

    def test_packet_received_should_increment_id(self):
        assert self.probe.id == 0
        self.probe.receive_packet()
        assert self.probe.id == 1

    def test_upon_receiving_packet_should_respond_to_server_with_concat_id(self):
        self.probe.sock.recv.return_value = '1'.encode()
        self.probe.receive_packet()

        self.probe.sock.sendto.assert_called_once_with('1_0'.encode(), self.probe.server_address)

    def test_is_packet_loss_should_return_true(self):
        self.probe.old_id = 4

        assert self.probe.is_packet_loss('5')

    def test_is_packet_loss_should_return_false(self):
        self.probe.old_id = 7

        assert not self.probe.is_packet_loss('7')
