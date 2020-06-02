import argparse
from .watch_command import watch_command
import logging

parser = argparse.ArgumentParser(
    prog="prepl",
    description="""
Autorun command on file change.
""",
)
parser.add_argument(
    "command",
    nargs=argparse.REMAINDER,
    help="the command to run and any arguments",
    metavar="COMMAND ...",
)
parser.add_argument(
    "-c",
    help="command string to run in shell (alternative to COMMAND ...)",
    metavar="COMMAND_STRING",
)
parser.add_argument("--debug", help=argparse.SUPPRESS, action="store_true")


def main(args=None):

    args = parser.parse_args(args)

    logging_kwargs = {}
    logging_kwargs["level"] = "DEBUG" if args.debug else "INFO"

    if not args.debug:
        logging_kwargs["format"] = "(prepl) %(message)s"

    logging.basicConfig(**logging_kwargs)

    if args.c is not None:
        if args.command:
            parser.error("a command and command string can not both be specified")

        command = args.c
        shell = True
    elif args.command:
        command = args.command
        shell = False
    else:
        parser.error("a command must be specified")

    try:
        watch_command(command, shell=shell)
    except KeyboardInterrupt:
        print("")
