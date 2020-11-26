from argparse import ArgumentParser

import pytest

from steinloss.stein_parser import setup


def args(arr, mocker):
    argv = ('steinloss ' + arr).split(' ')
    mocker.patch("sys.argv", new=argv)


class TestParser:

    def setup_method(self):
        std_parser = ArgumentParser()
        self.parser = setup(std_parser)

    def test_stein_parser_stores_server_variable(self, mocker):
        args('--server', mocker)

        parser = self.parser.parse_args()

        assert parser.server

    def test_stein_parser_server_abbreviation_returns_true(self, mocker):
        args('-s', mocker)

        self.parser.print_help()
        parser = self.parser.parse_args()

        assert parser.server

    def test_stein_parser_probe_variable(self, mocker):
        args('--probe -i 0.0.0.0', mocker)

        parser = self.parser.parse_args()

        assert parser.probe

    def test_stein_parser_probe_abbreviation_returns_true(self, mocker):
        args('-p -i 0.0.0.0', mocker)

        parser = self.parser.parse_args()

        assert parser.probe

    def test_raises_exit_when_neither_server_or_probe_is_selected(self, mocker):
        args('', mocker)

        with pytest.raises(SystemExit):
            parser = self.parser.parse_args()

    def test_default_port_is_set(self, mocker):
        args('-s', mocker)

        parser = self.parser.parse_args()

        assert isinstance(parser.port, int)

    def test_probe_exits_if_no_ip_is_provided(self, mocker):
        args('--probe', mocker)

        # Make parser after mocked arguments. Every test should look like this, but it made all the other test readable.
        # This mocks the scenario better, as the setup method is called after the arguments are given
        std_parser = ArgumentParser()
        self.parser = setup(std_parser)

        with pytest.raises(SystemExit):
            self.parser.parse_args()
