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

    def test_iterate_through_window_twice_without_loss(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))
        window_size = 5

        for n in range(0, window_size * 2):
            probe.consume_packet(str(n))

        assert probe.lost == 0

    def test_count_loss_when_out_of_reorder_window(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.consume_packet('0')
        probe.consume_packet('5')

        # lost package 1,2
        # package 3,4 is still in reordering window
        assert probe.lost == 2

    def test_is_packet_loss_should_handle_reordering(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('1')

        assert probe.lost == 0

    def test_no_packet_loss_inside_window(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('3')
        probe.consume_packet('1')
        probe.consume_packet('4')

        assert probe.lost == 0

    def test_package_outside_reorder_window_do_not_get_counted(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('3')
        probe.consume_packet('4')

        # not in reorder window
        probe.consume_packet('1')

        assert probe.lost == 1

    def test_detect_loss(self, mocker):
        mocker.patch('socket.socket')
        probe = Probe(('fake_address', 1337))

        probe.consume_packet('1')
        probe.consume_packet('0')
        probe.consume_packet('2')
        probe.consume_packet('4')
        probe.consume_packet('5')
        probe.consume_packet('6')

        assert probe.lost == 1
