def log(*str, **kwargs):
    print(bcolors.GREEN, "[SOCKET]", *str, bcolors.DEFAULT, **kwargs)


class bcolors:
    GREEN = '\033[92m'
    DEFAULT = '\033[0m'
