import pytest
import pandas as pd

from src.dashboard.dashboard_util import Data_Presenter


class Test_Dashboard:
    def setup_method(self):
        self.server_values = pd.read_csv('test_server.csv')
        self.client_values = pd.read_csv('test_client.csv')

    def teardown_method(self):
        Data_Presenter.clear_instance()

    def test_data_presenter_can_be_instantiated(self):
        my_singleton = Data_Presenter()
        assert my_singleton is not None

    def test_data_presenter_can_take_an_argument(self):
        test_data = [1, 2, 3]
        data_presenter = Data_Presenter()
        data_presenter.append(test_data)

        assert data_presenter.data == test_data

    def test_data_presenter_instance_is_stored_as_a_class_variable(self):
        data_presenter = Data_Presenter()

        assert Data_Presenter.get_instance() is not None

    def test_data_presenter_class_method_exposes_properties(self):
        test_data = [1, 2, 3]
        data_presenter = Data_Presenter()
        data_presenter.append(test_data)

        assert Data_Presenter.get_instance().data == test_data

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

        test_data = [1, 2, 3]
        data_presenter1.append(test_data)

        from_different_object = data_presenter2.read()

        assert from_different_object == test_data

    def test_append_method_appends_data(self):
        data_presenter = Data_Presenter.get_instance()
        test_data_1 = [1, 2, 3]
        test_data_2 = [4, 5, 6]

        data_presenter.append(test_data_1)
        data_presenter.append(test_data_2)

        assert data_presenter.read() == [1, 2, 3, 4, 5, 6]

    def test_continuous_data(self):
        data_presenter = Data_Presenter.get_instance()
        test_data_1 = [1, 2, 3]
        test_data_2 = [4, 5, 6]
        data_presenter.append(test_data_1)

        first_read = data_presenter.read()
        data_presenter.append(test_data_2)
        second_read = data_presenter.read()

        assert first_read == test_data_1
        assert second_read == test_data_2
