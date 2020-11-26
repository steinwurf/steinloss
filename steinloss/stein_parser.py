from argparse import ArgumentParser
import sys


def setup(parser: ArgumentParser) -> ArgumentParser:
    parser.description = \
        "A tool for measuring a package loss, between two endpoints. The way it works, is by spinning up a server " \
        "endpoint, that waits for a incoming connection. When the server-side gets pinged by a probe, it will start " \
        "sending packages to it, and the probe will respond on each packages." \
        "The package loss is calculated by keeping track of the id of the packet." \
        "Data is shown on the a website on port 8080, on the server side"
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
                        help="Which port to use. Have to be the same, as the servers port",
                        metavar='')  # Removes caps var name.

    return parser


def cli():
    parser = setup(ArgumentParser())
    parser.parse_args()
