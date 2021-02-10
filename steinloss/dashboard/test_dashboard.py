from datetime import datetime

from steinloss.loss_calculator import packet_table
from .dashboard import prep_data


def test_prep_data():
    date = datetime(2020, 1, 1)
    table = packet_table()
    table['a'].sent_at = date
    table['a'].received_at = date
    table['b'].sent_at = date
    table['b'].received_at = date

    res = list(prep_data(table))

    expected = [['2020-01-01_00:00:00', '2020-01-01_00:00:00'], ['2020-01-01_00:00:00', '2020-01-01_00:00:00']]
    assert res == expected


def test_if_recv_at_is_null():
    date = datetime(2020, 1, 1)
    table = packet_table()
    table['a'].sent_at = date
    # table['a'].received_at = date

    res = list(prep_data(table))

    expected = [['2020-01-01_00:00:00', '']]
    assert res == expected
