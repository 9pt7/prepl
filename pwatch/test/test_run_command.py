from pwatch.run_command import run_command, FileEvent


def test_cat(unwatched_file):
    events = run_command(["cat", str(unwatched_file)])
    assert FileEvent(str(unwatched_file), True) in events


def test_touch(unwatched_file):
    events = run_command(["touch", str(unwatched_file)])
    assert FileEvent(str(unwatched_file), False) in events


def test_stat(unwatched_file):
    events = run_command(["stat", "-L", str(unwatched_file)])
    assert FileEvent(str(unwatched_file), True) in events


def test_lstat(unwatched_file):
    events = run_command(["stat", str(unwatched_file)])
    assert FileEvent(str(unwatched_file), True) in events


def test_unlink(unwatched_file):
    events = run_command(["unlink", str(unwatched_file)])
    assert FileEvent(str(unwatched_file), False) in events


def test_rm_r(tmp_path, unwatched_file):
    events = run_command(["rm", "-r", str(tmp_path)])
    assert FileEvent(str(unwatched_file), False) in events
