from datetime import datetime

import pytest
from freezegun import freeze_time

from steinloss.Data_Presenter import Data_Presenter
from steinloss.packet_entity import sent_package, receive_package


class TestDataPresenter:
    def teardown_method(self):
        Data_Presenter.clear_instance()

    def test_data_presenter_can_be_instantiated(self):
        my_singleton = Data_Presenter()
        assert my_singleton is not None

    def test_data_presenter_can_take_an_argument(self):
        test_data = sent_package("1")
        data_presenter = Data_Presenter.get_instance()

        data_presenter.append(test_data)

        assert data_presenter.latest_packages().pop().sent_at == test_data.time

    def test_data_presenter_instance_is_stored_as_a_class_variable(self):
        data_presenter = Data_Presenter()

        assert Data_Presenter.get_instance() is not None

    def test_data_presenter_cannot_be_initiated_twice(self):
        data_presenter = Data_Presenter()

        with pytest.raises(RuntimeError) as re:
            Data_Presenter()

        assert re

    def test_get_instance_initiates_the_class_if_not_initiated(self):
        data_presenter = Data_Presenter.get_instance()

        assert data_presenter is not None

    def test_data_from_different_get_instance(self):
        data_presenter1 = Data_Presenter.get_instance()
        data_presenter2 = Data_Presenter.get_instance()

        test_data = sent_package("1")
        data_presenter1.append(test_data)

        from_different_object = data_presenter2.latest_packages().pop()

        assert from_different_object.sent_at == test_data.time

    @freeze_time(auto_tick_seconds=1)
    def test_append_method_appends_data(self):
        data_presenter = Data_Presenter.get_instance()
        test_data_1 = sent_package("1")
        test_data_2 = receive_package("1", "1")

        data_presenter.append(test_data_1)
        data_presenter.append(test_data_2)

        latest = data_presenter.latest_packages().pop()
        assert latest.sent_at == test_data_1.time
        assert latest.received_at == test_data_2.time

    @freeze_time(auto_tick_seconds=1)
    def test_get_latest_data_by_amount_of_entries(self):
        data_presenter = Data_Presenter.get_instance()
        test_data_1 = sent_package("1")
        test_data_2 = sent_package("2")

        data_presenter.append(test_data_1)
        data_presenter.append(test_data_2)

        latest_package = data_presenter.latest_packages(1).pop()

        assert latest_package.sent_at == test_data_2.time

    def test_get_package_info_at_timestamp(self):
        data_presenter = Data_Presenter.get_instance()
        time = datetime.now()
        data_presenter.append(sent_package("1", time))
        data_presenter.append(sent_package("2", time))

        # get time table
        package_info = data_presenter.get_time_table()
        assert package_info[time].sent == 2
