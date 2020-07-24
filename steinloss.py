import sys
from src.probe import Probe
from src.server import Server


class TaskFactory:
    @staticmethod
    def create_task(first_arg):
        options = {
            's': Server,
            'p': Probe,
            'h': Help
        }
        if options[first_arg]() is None:
            return Help()
        return options[first_arg]()


class Steinloss:

    @staticmethod
    def run():
        task = TaskFactory.create_task(sys.argv[0])
        task.run()


class Help(object):
    def run(self):
        help_msg = """
        run the program with either '-p' for probe or '-s' for server
        """

        print(help_msg)


Steinloss.run()
