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


def test_is_packet_loss_should_detect_loss_when_the_next_id_is_more_than_three_numbers_higere(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.consume_packet('1')
    # lost package 2, 3, 4
    probe.consume_packet('5')

    assert probe.lost == 3


def test_is_packet_loss_should_handle_reordering(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.consume_packet('1')
    probe.consume_packet('3')
    probe.consume_packet('2')

    assert probe.lost == 0


def test_is_packet_loss_should_handle_reordering_down_to_three(mocker):
    mocker.patch('socket.socket')
    probe = Probe(('fake_address', 1337))

    probe.consume_packet('1')
    probe.consume_packet('3')
    probe.consume_packet('4')
    probe.consume_packet('5')

    # not in reorder window
    probe.consume_packet('2')

    assert probe.lost == 1
