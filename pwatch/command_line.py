import argparse
from .watch_command import watch_command

parser = argparse.ArgumentParser(
    prog="pwatch",
    usage="%(prog)s [-h] command [args ...]",
    description="""
    Autorun command on file change.
    """,
)
parser.add_argument("command", help="the command to run")
parser.add_argument(
    "args", nargs=argparse.REMAINDER, help="additional arguments for command"
)


def main(args=None):

    args = parser.parse_args(args)
    try:
        watch_command([[args.command] + args.args])
    except KeyboardInterrupt:
        print("")
