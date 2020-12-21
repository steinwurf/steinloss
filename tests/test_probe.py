from steinloss.probe import Probe


class TestProbe:

    def test_packet_received_should_increment_id(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        assert probe.id == 0
        probe.receive_packet()
        assert probe.id == 1

    def test_upon_receiving_packet_should_respond_to_server_with_concat_id(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.sock.recv.return_value = '1'.encode()
        probe.receive_packet()

        probe.sock.sendto.assert_called_once_with('1_0'.encode(), probe.server_address)
