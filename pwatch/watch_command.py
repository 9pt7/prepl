import subprocess

from .watch import Watch
from .run_command import run_command


def watch_command(cmds):
    while True:
        with Watch() as watch:
            blacklist = set()

            def _event_handler(evt):
                if evt.readonly:
                    if evt.path not in blacklist:
                        watch.watch(evt.path)
                else:
                    blacklist.add(str(evt.path))

            try:
                for cmd in cmds:
                    print(f"> {' '.join(cmd)}")
                    run_command(cmd, _event_handler)
            except subprocess.CalledProcessError as err:
                print(f"> {err}")

            while True:
                file_list = [
                    str(f) for f in watch.wait_for_events() if str(f) not in blacklist
                ]

                if len(file_list) > 0:
                    break
