import sys
from threading import Thread

from steinloss.dashboard import dashboard
from steinloss.probe import Probe
from steinloss.server import Server


class TaskFactory:
    @staticmethod
    def create_task():
        first_arg = sys.argv[1] if len(sys.argv) > 1 else 'help'
        if first_arg == 's':
            return FrontEndAndBackEnd()
        elif first_arg == 'p':
            return Probe(('10.0.0.1', 7070))
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


class FrontEndAndBackEnd:

    def run(self):
        server = Server()
        t = Thread(target=server.run)
        t.start()

        dashboard.run()

        t.join()


Steinloss.run()
