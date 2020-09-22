from src.probe import Probe


def test_packet_received_should_increment_id(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    assert probe.id == 0
    probe.receive_packet()
    assert probe.id == 1


def test_upon_receiving_packet_should_respond_to_server_with_concat_id(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.sock.recv.return_value = '1'.encode()
    probe.receive_packet()

    probe.sock.sendto.assert_called_once_with('1_0'.encode(), probe.server_address)


def test_is_packet_loss_should_return_true(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.id_on_last_received_packet = 4

    assert probe.is_packet_loss('5')


def test_is_packet_loss_should_return_false(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.id_on_last_received_packet = 7

    # skipped packet 8
    assert not probe.is_packet_loss('9')
