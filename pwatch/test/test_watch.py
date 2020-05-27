import pytest
import uuid
import shutil


def modify(path):
    print("MODIFY")
    with open(path, "w") as fil:
        fil.write(str(uuid.uuid4()))


TIMEOUT = 10e-3


def check_events(watch):
    watch.wait_for_events(TIMEOUT)


def check_no_events(watch):
    with pytest.raises(TimeoutError):
        check_events(watch)


def test_modify_file(watch, file1):
    watch.watch(file1)

    # Should not get event prior to edit
    check_no_events(watch)

    modify(file1)

    # Should get event for edit

    check_events(watch)


def test_modify_unwatched_in_same_dir_as_watched(watch, file1, file2):
    watch.watch(file1)

    # Should not get event because path2 not being watched
    modify(file2)
    check_no_events(watch)


def test_unlink(watch, file1):
    watch.watch(file1)

    # Check for event after unlinking
    file1.unlink()
    check_events(watch)


def test_event_on_close(watch, file1):
    with open(file1, "wb", buffering=0) as f:
        watch.watch(file1)

        check_no_events(watch)

        f.write(b"hello world")

        check_no_events(watch)

    check_events(watch)


def test_remove_dir(watch, subdir1, subdir1_file1):
    watch.watch(subdir1_file1)
    shutil.rmtree(subdir1)
    check_events(watch)


def test_move_replace(watch, file1, file2):
    watch.watch(file1)
    check_no_events(watch)

    file2.rename(file1)
    check_events(watch)


def test_move_replace_from_other_dir(watch, subdir1_file1, subdir2_file1):
    watch.watch(subdir1_file1)
    check_no_events(watch)

    subdir2_file1.rename(subdir1_file1)
    check_events(watch)
