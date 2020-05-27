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


def test_modify_unwatched_in_same_dir_as_watched(watch, watched_file, unwatched_file):
    # Should not get event because path2 not being watched
    modify(unwatched_file)
    check_no_events(watch)


def test_unlink(watch, watched_file):
    # Check for event after unlinking
    watched_file.unlink()
    check_events(watch)


def test_event_on_close(watch, watched_file):
    with open(watched_file, "wb", buffering=0) as f:
        check_no_events(watch)

        f.write(b"hello world")

        check_no_events(watch)

    check_events(watch)


def test_remove_dir(watch, subdir1, subdir1_file1):
    watch.watch(subdir1_file1)
    shutil.rmtree(subdir1)
    check_events(watch)


def test_move_replace(watch, watched_file, unwatched_file):
    watch.watch(watched_file)
    check_no_events(watch)

    unwatched_file.rename(watched_file)
    check_events(watch)


def test_move_replace_from_other_dir(watch, subdir1_file1, subdir2_file1):
    watch.watch(subdir1_file1)
    check_no_events(watch)

    subdir2_file1.rename(subdir1_file1)
    check_events(watch)
