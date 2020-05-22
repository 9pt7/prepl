from pathlib import Path
import inotify_simple


class Watch(object):
    def __enter__(self):
        self.__inotify = inotify_simple.INotify()
        self.__watches = dict()
        self.__files = set()
        return self

    def __exit__(self, type, value, traceback):
        self.__inotify.close()

    def watch(self, path):

        path = Path(path).resolve()

        if path in self.__files:
            return

        path_to_watch = path.parent if path.is_file() else path

        if not path_to_watch.is_dir():
            return

        flags = inotify_simple.flags.DELETE | inotify_simple.flags.MODIFY
        wd = self.__inotify.add_watch(path_to_watch, flags)

        self.__watches[wd] = path_to_watch
        self.__files.add(path)

    def wait_for_event(self):

        while True:
            for event in self.__inotify.read():
                dir_path = self.__watches[event.wd]
                path = dir_path / event.name

                if path in self.__files:
                    return path
