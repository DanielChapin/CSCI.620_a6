from argparse import ArgumentParser
from dataclasses import dataclass, field
from sys import argv
from typing import Any, Callable


@dataclass
class MainArgs:
    load: bool = True
    init: bool = True
    scale: bool = True
    analyze: bool = True
    cluster: bool = True


def parser() -> ArgumentParser:
    p = ArgumentParser()

    p.add_argument('--no-load', dest='load', action='store_false',
                   help="Don't load data into tables.")
    p.add_argument('--no-init', dest='init', action='store_false',
                   help="Don't drop and re-add tables.")
    p.add_argument('--no-analyze', dest='analyze', action='store_false',
                   help="Dont't perform analysis of dataset.")
    p.add_argument('--no-scale', dest='scale', action='store_false',
                   help="Don't perform scaling on dataset.")
    p.add_argument('--no-cluster', dest='cluster', action='store_false',
                   help="Don't perform clustering.")

    return p


def args(argv: list[str] = argv):
    return parser().parse_args(argv[1:], namespace=MainArgs())


def entrypoint(fn: Callable[[MainArgs], Any]) -> Any:
    return fn(args())
