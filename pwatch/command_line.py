import argparse
from .watch_command import watch_command
import logging

parser = argparse.ArgumentParser(
    prog="pwatch",
    description="""
    Autorun command on file change.
    """,
)
parser.add_argument("command", nargs=argparse.REMAINDER, help="the command to run")
parser.add_argument("-c", help="string to run in shell", metavar="COMMAND_STRING")
parser.add_argument("--debug", help="use debug-level logging", action="store_true")


def main(args=None):

    args = parser.parse_args(args)

    logging_kwargs = {}
    logging_kwargs["level"] = "DEBUG" if args.debug else "INFO"

    if not args.debug:
        logging_kwargs["format"] = "> %(message)s"

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
