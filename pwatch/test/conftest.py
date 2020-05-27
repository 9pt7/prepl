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


@pytest.fixture
def subdir1(tmp_path):
    subdir1 = tmp_path / "subdir1"
    subdir1.mkdir()
    return subdir1


@pytest.fixture
def subdir1_file1(subdir1):
    subdir1_file1 = subdir1 / "file1.txt"
    subdir1_file1.touch()
    return subdir1_file1


@pytest.fixture
def subdir2(tmp_path):
    subdir2 = tmp_path / "subdir2"
    subdir2.mkdir()
    return subdir2


@pytest.fixture
def subdir2_file1(subdir2):
    subdir2_file1 = subdir2 / "file1.txt"
    subdir2_file1.touch()
    return subdir2_file1
