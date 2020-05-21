import argparse
from .watch_command import watch_command


def main(args=None):
    parser = argparse.ArgumentParser(
        description="""
    Autorun commannd on file change
    """
    )
    parser.add_argument("command")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args(args)
    try:
        watch_command([[args.command] + args.args])
    except KeyboardInterrupt:
        print("")


if __name__ == "__main__":
    main()
