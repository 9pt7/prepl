import os
import inotify_simple
from pathlib import Path


class Watch(object):
    def __enter__(self):
        self.__inotify = inotify_simple.INotify()
        self.__watches = dict()
        self.__watch_path = dict()
        return self

    def __exit__(self, type, value, traceback):
        self.__inotify.close()

    def watch(self, path):

        path_to_watch, name = os.path.split(os.path.abspath(path))

        flags = inotify_simple.flags.DELETE | inotify_simple.flags.MODIFY
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

    def wait_for_events(self):

        while True:
            event_list = [
                self.__watch_path[evt.wd] / evt.name
                for evt in self.__inotify.read()
                if evt.name in self.__watches[evt.wd]
            ]

            if len(event_list) > 0:
                return event_list
