import subprocess

from .watch import Watch
from .run_command import run_command


def watch_command(cmds):
    while True:
        with Watch() as watch:
            blacklist = set()

            def _event_handler(evt):
                if evt.readonly:
                    if evt.path.is_file() and evt.path not in blacklist:
                        watch.watch(evt.path)
                else:
                    blacklist.add(evt.path)

            try:
                for cmd in cmds:
                    print(f"> {' '.join(cmd)}")
                    run_command(cmd, _event_handler)
            except subprocess.CalledProcessError as err:
                print(f"> {err}")

            while True:
                modified_file = watch.wait_for_event()
                if modified_file not in blacklist:
                    break
