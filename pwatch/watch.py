import queue
from pathlib import Path

import watchdog
import watchdog.observers
import watchdog.events


class _EventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, on_any_event):
        super().__init__()
        self.on_any_event = on_any_event


class Watch(object):
    def __init__(self):
        super().__init__()
        self.__queue = queue.SimpleQueue()
        self.__files = set()
        self.__obs = watchdog.observers.Observer()
        self.__handler = _EventHandler(self.__on_any_event)

    def __enter__(self):
        self.__obs.start()
        return self

    def __exit__(self, type, value, traceback):
        self.__obs.stop()
        self.__obs.join()

    def watch(self, path):

        path = Path(path).resolve()

        path_to_watch = path.parent if path.is_file() else path

        if not path_to_watch.is_dir():
            return

        if path in self.__files:
            return

        self.__obs.schedule(self.__handler, str(path_to_watch))
        self.__files.add(path)

    def __on_any_event(self, event):
        path = Path(event.src_path).resolve()
        self.__queue.put(path)

    def wait_for_event(self):
        while True:
            path = self.__queue.get()
            if path in self.__files:
                return path
