import asyncio
from pathlib import Path
import socket


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


async def repeat(func, interval=None, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    if interval is None:
        while True:
            await asyncio.gather(func(*args, **kwargs))
    else:
        while True:
            await asyncio.gather(
                func(*args, **kwargs),
                asyncio.sleep(interval),
            )


if __name__ == '__main__':
    UDP_IP = "127.0.0.1"
    UDP_PORT = 7070
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    sock.sendto('go'.encode(), (UDP_IP, 7071))

    id = 0
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data.decode(), end='\r')
        data = data.decode() + f"_{id}"
        id += 1
        sock.sendto(data.encode(), (UDP_IP, 7071))
