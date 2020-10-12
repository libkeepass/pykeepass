from argparse import ArgumentParser
from pykeepass import __version__


def main():
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
