import logging
from .watch import Watch
from .run_command import run_command

logger = logging.getLogger(__name__)


def watch_command(cmd, shell=False):
    while True:
        with Watch() as watch:
            blacklist = set()

            def _event_handler(evt):
                if evt.readonly:
                    if evt.path not in blacklist:
                        watch.watch(evt.path)
                else:
                    blacklist.add(str(evt.path))

            run_command(cmd, _event_handler, shell)

            logger.info("waiting for file change...")
            while True:
                file_list = [
                    str(f) for f in watch.wait_for_events() if str(f) not in blacklist
                ]

                for f in file_list:
                    logger.info(f"file changed: {f}")

                if len(file_list) > 0:
                    break
