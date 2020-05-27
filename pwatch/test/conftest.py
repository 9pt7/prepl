from pwatch.watch import Watch
import pytest


@pytest.fixture
def watch():
    with Watch() as w:
        yield w


@pytest.fixture
def file1(tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.touch()
    return file1


@pytest.fixture
def file2(tmp_path):
    file2 = tmp_path / "file2.txt"
    file2.touch()
    return file2


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
