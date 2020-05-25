import os
import inotify_simple
from pathlib import Path
import itertools


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

    def watch(self, path):

        path_to_watch, name = os.path.split(os.path.abspath(path))

        flags = (
            inotify_simple.flags.DELETE
            | inotify_simple.flags.CLOSE_WRITE
            | inotify_simple.flags.MOVED_TO
        )
        try:
            wd = self.__inotify.add_watch(path_to_watch, flags)
        except FileNotFoundError:
            pass
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
            if err_events:
                # TODO
                print(err_events)
            file_events = [evt for evt in events if evt.wd >= 0]

            event_dirs = list(
                itertools.chain(
                    *(
                        [
                            self.__watch_path[evt.wd] / name
                            for name in self.__watches[evt.wd]
                        ]
                        for evt in file_events
                        if not evt.name
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
