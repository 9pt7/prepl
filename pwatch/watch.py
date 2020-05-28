import os
import inotify_simple
from pathlib import Path
import itertools
import logging

logger = logging.getLogger(__name__)


class Watch(object):
    def init(self):
        self.__inotify = inotify_simple.INotify()
        self.__watches = dict()
        self.__watch_path = dict()

    def close(self):
        self.__inotify.close()

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def max_queued_events(self):
        with open("/proc/sys/fs/inotify/max_queued_events", "r") as f:
            return int(f.read())

    def watch(self, path):

        path = Path(path)

        # We only want to watch valid, regular files
        if not path.is_file():
            return

        path_to_watch, name = os.path.split(os.path.abspath(path))

        flags = (
            inotify_simple.flags.DELETE
            | inotify_simple.flags.CLOSE_WRITE
            | inotify_simple.flags.MOVED_TO
            | inotify_simple.flags.MOVED_FROM
        )
        try:
            wd = self.__inotify.add_watch(path_to_watch, flags)
        except FileNotFoundError as err:
            logger.warning(f"inotify_add_watch: {err}")
        else:
            s_default = set()
            s = self.__watches.setdefault(wd, s_default)
            s.add(name)
            if s is s_default:
                self.__watch_path[wd] = Path(path_to_watch).resolve()

    def wait_for_events(self, timeout=None):

        if timeout is not None:
            timeout = round(timeout * 1000)

        while True:
            events = list(self.__inotify.read(timeout))
            err_events = [evt for evt in events if evt.wd < 0]
            for evt in err_events:
                logger.warning(f"inotify event error: {evt}")
            valid_events = [evt for evt in events if evt.wd >= 0]

            dir_events = [evt for evt in valid_events if not evt.name]
            file_events = [evt for evt in valid_events if evt.name]

            for evt in dir_events:
                logger.debug(f"dir event: {self.__watch_path[evt.wd]}")

            for evt in file_events:
                logger.debug(f"file event: {self.__watch_path[evt.wd] / evt.name}")

            event_dirs = list(
                itertools.chain(
                    *(
                        [
                            self.__watch_path[evt.wd] / name
                            for name in self.__watches[evt.wd]
                        ]
                        for evt in dir_events
                    )
                )
            )

            event_files = [
                self.__watch_path[evt.wd] / evt.name
                for evt in file_events
                if evt.name in self.__watches[evt.wd]
            ]

            event_list = event_dirs + event_files

            if not event_list:
                # No events returned
                if timeout is not None:
                    raise TimeoutError()
            else:
                return event_list
