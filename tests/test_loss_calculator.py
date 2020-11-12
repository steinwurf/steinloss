from freezegun import freeze_time
from datetime import datetime, timedelta

from steinloss.loss_calculator import Loss_Calculator, TimeTable
from steinloss.packet_entity import sent_package, receive_package


class TestLossCalculator:
    def test_initiate_loss_calculator(self):
        Loss_Calculator()

    def test_loss_calculator_can_add_packet_entry(self, freezer):
        loss_calculator = Loss_Calculator()
        packet = sent_package('1', datetime.now())

        loss_calculator.add(packet)

        assert packet in loss_calculator

    @freeze_time("00:00:00", auto_tick_seconds=1)
    def test_two_entries_with_more_than_a_second_apart_should_not_be_in_same_key(self, freezer):
        loss_calculator = Loss_Calculator()
        first_time = datetime.now()
        second_time = datetime.now()

        packet_one = sent_package('1', first_time)
        packet_two = sent_package('2', second_time)
        loss_calculator.add(packet_one)
        loss_calculator.add(packet_two)

        assert loss_calculator[first_time].sent == 1
        assert loss_calculator[second_time].sent == 1

    @freeze_time("00:00:00", auto_tick_seconds=0.5)
    def test_loss_calculator_can_add_two_entries_at_same_timestamp(self, freezer):
        loss_calculator = Loss_Calculator()
        at_zero_second = datetime.now()
        at_zero_point_5_second = datetime.now()
        packet_at_zero_second = sent_package('1', at_zero_second)
        packet_at_zero_point_5_second = sent_package('2', at_zero_point_5_second)

        loss_calculator.add(packet_at_zero_second)
        loss_calculator.add(packet_at_zero_point_5_second)

        assert loss_calculator[at_zero_second].sent == 2

    def test_loss_calculator_counts_sent_packages_at_timestamp(self):
        loss_calculator = Loss_Calculator()
        time_stamp = datetime.now()

        loss_calculator.add(sent_package('1', time_stamp))
        loss_calculator.add(sent_package('2', time_stamp))

        assert loss_calculator[time_stamp].sent == 2

    def test_loss_calculator_counts_received_packages_at_timestamp(self):
        loss_calculator = Loss_Calculator()
        time_stamp = datetime.now()

        loss_calculator.add(sent_package('1', time_stamp))
        loss_calculator.add(receive_package('1', '1', time_stamp))

        assert loss_calculator[time_stamp].received == 1

    def test_loss_calculator_counts_loss_when_packet_do_not_return(self):
        loss_calculator = Loss_Calculator()
        time_stamp = datetime.now()

        loss_calculator.add(sent_package('1', time_stamp))
        loss_calculator.add(sent_package('2', time_stamp))
        loss_calculator.add(sent_package('3', time_stamp))

        loss_calculator.add(receive_package('1', '1', time_stamp))
        loss_calculator.add(receive_package('3', '2', time_stamp))

        assert loss_calculator[time_stamp].loss == 1

    def test_sent_package_added_to_calculator_is_logged(self):
        loss_calculator = Loss_Calculator()
        time_stamp = datetime.now()
        package = sent_package('1', time_stamp)

        loss_calculator.add(package)

        assert loss_calculator[package.id].is_sent()

    def test_sent_package_added_to_calculator_is_not_received(self):
        loss_calculator = Loss_Calculator()
        time_stamp = datetime.now()
        package = sent_package('1', time_stamp)

        loss_calculator.add(package)

        assert not loss_calculator[package.id].is_received()

    @freeze_time("00:00:00")
    def test_convert_datetime_max_value_for_rounding_down(self):
        time_table = TimeTable()

        # 1000 milliseconds = 1 second
        at_999_milliseconds = datetime.now() + timedelta(milliseconds=999)
        at_0_second_string = time_table.convert_time_to_key(at_999_milliseconds)

        assert at_0_second_string == "00:00:00"

    @freeze_time("00:00:00")
    def test_convert_datetime_returns_seconds_in_string(self):
        time_table = TimeTable()

        # 1000 milliseconds = 1 second
        at_1_milliseconds = datetime.now() + timedelta(seconds=1)
        at_1_second_string = time_table.convert_time_to_key(at_1_milliseconds)

        assert at_1_second_string == "00:00:01"

    def test_get_last_package(self):
        loss_calculator = Loss_Calculator()

        package = sent_package("1")
        loss_calculator.add(package)

        last_package = loss_calculator.get_last_packages(1).pop()
        assert last_package.sent_at == package.time

    def test_get_n_latest_packages_where_n_is_equal_to_length(self):
        loss_calculator = Loss_Calculator()
        loss_calculator.add(sent_package("1"))
        loss_calculator.add(sent_package("2"))

        packages = loss_calculator.get_last_packages(2)

        assert len(packages) == 2

    @freeze_time(auto_tick_seconds=1)
    def test_get_n_latest_packages(self):
        loss_calculator = Loss_Calculator()
        p1 = sent_package("1", datetime.now())
        p2 = sent_package("2")
        p3 = sent_package("3")

        loss_calculator.add(p1)
        loss_calculator.add(p2)
        loss_calculator.add(p3)

        packages = loss_calculator.get_last_packages(2)

        assert not any(pack.sent_at == p1.time for pack in packages)
        assert any(pack.sent_at == p2.time for pack in packages)
        assert any(pack.sent_at == p3.time for pack in packages)

    # Test ideas:
    # what happens after 24H
