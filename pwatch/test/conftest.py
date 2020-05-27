from pwatch.watch import Watch
import pytest


@pytest.fixture
def watch():
    with Watch() as w:
        yield w


@pytest.fixture
def watched_file(watch, tmp_path):
    watched_file = tmp_path / "watched_file.txt"
    watched_file.touch()
    watch.watch(watched_file)
    return watched_file


@pytest.fixture
def unwatched_file(tmp_path):
    unwatched_file = tmp_path / "unwatched_file.txt"
    unwatched_file.touch()
    return unwatched_file
