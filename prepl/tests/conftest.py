from prepl.watch import Watch
import pytest
from pathlib import Path
import os


def absolute(path):
    return Path(path).absolute()


def relative(path):
    return Path(os.path.relpath(path))


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


@pytest.fixture(params=[absolute, relative])
def unwatched_file(request, tmp_path):
    unwatched_file = tmp_path / "unwatched_file.txt"
    unwatched_file.touch()
    return request.param(unwatched_file)


@pytest.fixture
def watched_invalid_file(watch):
    path = "/dev/null"
    watch.watch(path)
    return path
