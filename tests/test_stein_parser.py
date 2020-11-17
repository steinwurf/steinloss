from argparse import ArgumentParser

import pytest

from src.stein_parser import setup


class TestParser:

    def setup_method(self):
        std_parser = ArgumentParser()
        self.parser = setup(std_parser)

    def test_stein_parser_stores_server_variable(self):
        args = ['--server']

        parser = self.parser.parse_args(args)

        assert parser.server

    def test_stein_parser_server_abbreviation_returns_true(self):
        args = ['-s']

        self.parser.print_help()
        parser = self.parser.parse_args(args)

        assert parser.server

    def test_stein_parser_probe_variable(self):
        args = "--probe 0.0.0.0".split(' ')

        parser = self.parser.parse_args(args)

        assert parser.probe

    def test_stein_parser_probe_abbreviation_returns_true(self):
        args = '-p 0.0.0.0'.split(' ')

        parser = self.parser.parse_args(args)

        assert parser.probe

    def test_raises_exit_when_neither_server_or_probe_is_selected(self):
        args = []

        with pytest.raises(SystemExit):
            parser = self.parser.parse_args(args)

    def test_default_port_is_set(self):
        args = ['-s']

        parser = self.parser.parse_args(args)

        assert isinstance(parser.port, int)

    def test_probe_exits_if_no_ip_is_provided(self):
        args = ['-p']

        with pytest.raises(SystemExit):
            parser = self.parser.parse_args(args)
