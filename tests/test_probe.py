import pickle
from datetime import datetime
import pytest
from src.probe import Probe


def _receive_packet_should_save_all_received_packets(mocker, freezer):
    mocker.patch('socket.socket.recv', return_value='fake_id')

    probe = Probe()
    probe.receive_packet()

    assert len(probe.packets_received) == 1
    expected = 'fake_id', datetime.now()
    assert probe.packets_received.pop() == expected


def _encode_packets_should_return_binary_string():
    probe = Probe()
    test_packets = [('1', datetime.now()), ('2', datetime.now())]
    probe.packets_received = test_packets
    actual = pickle.dumps(test_packets)

    assert len(probe.packets_received)
    assert probe.encode_packets() == actual


@pytest.mark.asyncio
async def test_log_should_send_packets_to_server_using_pickle(mocker, freezer):
    freezer.move_to('2020-08-08')
    test_packets = [('1', datetime.now()), ('2', datetime.now())]
    mocked_tcp_send = mocker.patch('socket.socket.send')

    probe = Probe()
    probe.packets_received = test_packets
    await probe.log_packets_to_server()

    assert probe.packets_received == []
    mocked_tcp_send.assert_called_with(pickle.dumps(test_packets))
