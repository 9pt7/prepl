from pwatch.watch import Watch
import tempfile
from pathlib import Path
from contextlib import contextmanager
import pytest
import uuid
import shutil


@contextmanager
def watch_test():
    watch = Watch()
    watch.init()
    try:
        tmp = tempfile.TemporaryDirectory()
        try:
            yield watch, Path(tmp.name)
        finally:
            tmp.cleanup()
    finally:
        watch.close()


def modify(path):
    with open(path, "w") as fil:
        fil.write(str(uuid.uuid4()))


TIMEOUT = 10e-3


def check_events(watch):
    watch.wait_for_events(TIMEOUT)


def check_no_events(watch):
    with pytest.raises(TimeoutError):
        check_events(watch)


def test_modify_file():
    with watch_test() as (watch, tmp):

        path = tmp / "file.txt"
        path.touch()

        assert path.is_file()

        watch.watch(path)

        # Should not get event prior to edit
        check_no_events(watch)

        modify(path)

        # Should get event for edit
        check_events(watch)


def test_modify_unwatched_in_same_dir_as_watched():
    with watch_test() as (watch, tmp):

        path = tmp / "file.txt"
        path.touch()
        watch.watch(path)

        path2 = tmp / "file2.txt"

        # Should not get event because path2 not being watched
        modify(path2)
        check_no_events(watch)


def test_unlink():
    with watch_test() as (watch, tmp):

        path = tmp / "file.txt"
        path.touch()
        watch.watch(path)

        # Check for event after unlinking
        path.unlink()
        check_events(watch)


def test_event_on_close():
    with watch_test() as (watch, tmp):

        path = tmp / "file.txt"

        with open(path, "wb", buffering=0) as f:
            watch.watch(path)

            check_no_events(watch)

            f.write(b"hello world")

            check_no_events(watch)

        check_events(watch)


def test_remove_dir():
    with watch_test() as (watch, tmp):

        subdir = tmp / "subdir"
        subdir.mkdir()

        path = subdir / "file.txt"
        watch.watch(path)

        shutil.rmtree(subdir)
        check_events(watch)
