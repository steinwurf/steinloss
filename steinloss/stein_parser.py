import sys
from argparse import Action
from argparse import ArgumentParser
from threading import Thread

from steinloss import __version__
from steinloss.dashboard import dashboard
from steinloss.probe import Probe
from steinloss.server import Server

kilobyte = 1024
mb = kilobyte * kilobyte


class SpeedConverter(Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.speeds = {
            '3mbps': mb * 3 / 8,
            '5mbps': mb * 5 / 8,
            '25mbps': mb * 25 / 8,
            '512kb': 512 * kilobyte,
            '4mb': 4 * mb,
            '8mb': 8 * mb,
            '16mb': 16 * mb
        }
        self.help = f"Choose from one of the preset speeds: {list(self.speeds.keys())}," \
                    " or input your own speed in a bytes/sec. Default is 4mb"

    def __call__(self, parser, namespace, values, option_string=None):
        if values not in self.speeds.keys():
            speed = int(values)
        elif values is None:
            speed = self.speeds['512kb']
        else:
            speed = self.speeds[values]

        setattr(namespace, self.dest, speed)


def setup(parser: ArgumentParser) -> ArgumentParser:
    parser.prog = "steinloss"
    parser.description = \
        "A tool for measuring a package loss, between two endpoints. The way it works, is by spinning up a server " \
        "endpoint, that waits for a incoming connection. When the server-side gets pinged by a probe, it will start " \
        "sending packages to it, and the probe will respond on each packages." \
        "The package loss is calculated by keeping track of the id of the packet." \
        "Data is shown on the a website on port 8080, on the server side"
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", action="store_true",
                       help="Determines if you're on the server side")
    group.add_argument("-p", "--probe", action="store_true",
                       help="Determines if you're on the probe side. "
                            "You have to specify a ip address for the probe to target")
    parser.add_argument("-i", "--ip-address", action="store", required='-p' in sys.argv or '--probe' in sys.argv,
                        help="REQUIRED for probe: the ip the probe pings. Server what it listens on",
                        metavar='')  # Removes caps var name.

    parser.add_argument("-P", "--port", type=int, default=9090,
                        help="Which port to use. Have to be the same, as the servers port. Default is 9090",
                        metavar='')  # Removes caps var name.
    parser.add_argument("--speed", action=SpeedConverter, default=4194304)  # 4mb

    return parser


def task_factory(options):
    if options.server:
        return FrontEndAndBackEnd(options.ip_address, options.port, options.speed)
    elif options.probe:
        return Probe(options.ip_address, options.port)
    else:
        return None


def cli():
    parser = setup(ArgumentParser())
    args = parser.parse_args()

    runnable = task_factory(args)
    runnable.run()


class FrontEndAndBackEnd:

    def __init__(self, ip, port, speed):
        self.kwargs = {}
        self.kwargs['port'] = port
        self.kwargs['speed'] = speed
        if ip is not None:
            self.kwargs['ip'] = ip

    def run(self):
        udp_socket = Server(**self.kwargs)
        t = Thread(target=udp_socket.run)
        try:
            t.start()
            dashboard.run()
        finally:
            t.join()
