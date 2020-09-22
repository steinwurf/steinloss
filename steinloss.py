import sys
from src.probe import Probe
from src.server import Server


class TaskFactory:
    @staticmethod
    def create_task():
        first_arg = sys.argv[1] if len(sys.argv) > 1 else 'help'
        if first_arg == 's':
            return Server.gigabyte()
        elif first_arg == 'p':
            return Probe(('192.168.0.107', 7070))
        else:
            return Help()


class Steinloss:

    @staticmethod
    def run():
        task = TaskFactory.create_task()
        task.run()


class Help(object):
    def run(self):
        help_msg = """
        run the program with either '-p' for probe or '-s' for server
        """

        print(help_msg)


Steinloss.run()
