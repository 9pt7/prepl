import pytest
import uuid
import shutil


def modify(path):
    with open(path, "w") as fil:
        fil.write(str(uuid.uuid4()))


TIMEOUT = 0


def check_events(watch):
    watch.wait_for_events(TIMEOUT)


def check_no_events(watch):
    with pytest.raises(TimeoutError):
        check_events(watch)


def test_modify_file(watch, watched_file):
    # Should not get event prior to edit
    check_no_events(watch)

    modify(watched_file)

    # Should get event for edit
    check_events(watch)


def test_modify_unwatched(watch, watched_file, unwatched_file):
    # Should not get event because unwatched file not being watched
    modify(unwatched_file)
    check_no_events(watch)


def test_unlink(watch, watched_file):
    # Check for event after unlinking
    watched_file.unlink()
    check_events(watch)


def test_unlink_unwatched(watch, watched_file, unwatched_file):
    # Check for event after unlinking
    unwatched_file.unlink()
    check_no_events(watch)


def test_event_on_close(watch, watched_file):
    with open(watched_file, "wb", buffering=0) as f:
        f.write(b"hello world")
        check_no_events(watch)
    check_events(watch)


def test_remove_dir(watch, tmp_path, watched_file):
    shutil.rmtree(tmp_path)
    check_events(watch)


def test_replace_watched(watch, watched_file, unwatched_file):
    check_no_events(watch)
    unwatched_file.rename(watched_file)
    check_events(watch)


def test_move_watched(watch, watched_file, unwatched_file):
    check_no_events(watch)
    watched_file.rename(unwatched_file)
    check_events(watch)


def test_watch_non_existing_dir(watch, tmp_path):
    watch.watch(tmp_path / "non_existing" / "path")
    check_no_events(watch)


def test_watch_invalid_path(watch, watched_invalid_file):
    check_no_events(watch)
    modify(watched_invalid_file)
    check_no_events(watch)
