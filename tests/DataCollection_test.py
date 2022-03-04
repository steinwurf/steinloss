import imp
from sqlite3 import DatabaseError
import pytest
from datetime import datetime
from steinloss.DataCollection import DataCollection
from steinloss.Package import SentPackage, ReceivePackage
from freezegun import freeze_time


class TestDataCollection:
    
    def teardown_method(self):
        DataCollection.clear()

    def test_instantiation(self):
        data_collection = DataCollection()
        assert data_collection is not None

    def test_singleton_property(self):
        data_collection1 = DataCollection()
        data_collection2 = DataCollection()

        assert data_collection2 == data_collection1


    def test_add_packet(self):
        data_collection = DataCollection()
        packet = SentPackage("1")

        data_collection.add(packet)

        assert packet in data_collection 


    def test_packet_appear_in_all_instances(self):
        data_collection1 = DataCollection()
        data_collection2 = DataCollection()
        packet = SentPackage("1") 

        data_collection1.add(packet)
        assert packet in data_collection2

    def test_last_packet_test(self):
        data_collection = DataCollection()
        test_packet_1 = SentPackage("1")
        test_packet_2 = ReceivePackage("1", "1")

        data_collection.add(test_packet_1)
        data_collection.add(test_packet_2)

        latest = data_collection.get_last_packages(1).pop()
        assert latest.sent_at == test_packet_1.time
        assert latest.received_at == test_packet_2.time


    #her
    @freeze_time("00:00:00", auto_tick_seconds=1)
    def test_two_entries_with_more_than_a_second_apart_should_not_be_in_same_key(self, freezer):
        data_collection = DataCollection()
        first_time = datetime.now()
        second_time = datetime.now()

        packet_one = SentPackage('1', first_time)
        packet_two = SentPackage('2', second_time)
        data_collection.add(packet_one)
        data_collection.add(packet_two)

        assert data_collection[first_time].sent == 1
        assert data_collection[second_time].sent == 1

    @freeze_time("00:00:00", auto_tick_seconds=0.5)
    def test_DataCollection_can_add_two_entries_at_same_timestamp(self, freezer):
        data_collection = DataCollection()
        at_zero_second = datetime.now()
        at_zero_point_5_second = datetime.now()
        packet_at_zero_second = SentPackage('1', at_zero_second)
        packet_at_zero_point_5_second = SentPackage('2', at_zero_point_5_second)

        data_collection.add(packet_at_zero_second)
        data_collection.add(packet_at_zero_point_5_second)

        assert data_collection[at_zero_second].sent == 2

    def test_loss_calculator_counts_sent_packages_at_timestamp(self):
        data_collection = DataCollection()
        time_stamp = datetime.now()

        data_collection.add(SentPackage('1', time_stamp))
        data_collection.add(SentPackage('2', time_stamp))

        assert data_collection[time_stamp].sent == 2


    def test_loss_calculator_counts_loss_when_packet_do_not_return(self):
        data_collection = DataCollection()
        time_stamp = datetime.now()

        data_collection.add(SentPackage('1', time_stamp))
        data_collection.add(SentPackage('2', time_stamp))
        data_collection.add(SentPackage('3', time_stamp))

        data_collection.add(ReceivePackage('1', '1', time_stamp))
        data_collection.add(ReceivePackage('3', '3', time_stamp))

        assert data_collection[time_stamp].loss == 1