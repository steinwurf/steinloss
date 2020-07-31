import sys
from src.probe import Probe
from src.server import Server


class TaskFactory:
    @staticmethod
    def create_task(first_arg):
        if first_arg == 's':
            return Server()
        elif first_arg == 'p':
            return Probe(('192.168.0.107', 7070))
        else:
            return Help()


class Steinloss:

    @staticmethod
    def run():
        task = TaskFactory.create_task(sys.argv[1])
        task.run()


class Help(object):
    def run(self):
        help_msg = """
        run the program with either '-p' for probe or '-s' for server
        """

        print(help_msg)


Steinloss.run()
