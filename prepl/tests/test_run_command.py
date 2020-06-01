from prepl.run_command import run_command, FileEvent
import subprocess
import json
from pathlib import Path
import pytest

test_helper = str(Path(__file__).parent / "test_helper")

commands = json.loads(subprocess.check_output(test_helper))


@pytest.fixture(params=commands["readcmds"])
def readcmd(request, unwatched_file):
    return [test_helper, request.param, unwatched_file]


@pytest.fixture(params=commands["editcmds"])
def editcmd(request, unwatched_file):
    return [test_helper, request.param, unwatched_file]


def test_readcmd(readcmd, unwatched_file):
    events = run_command(readcmd)
    assert FileEvent(str(Path(unwatched_file).resolve()), True) in events


def test_editcmd(editcmd, unwatched_file):
    events = run_command(editcmd)
    assert FileEvent(str(Path(unwatched_file).resolve()), False) in events


def test_cat(unwatched_file):
    events = run_command(["cat", str(unwatched_file)])
    assert FileEvent(str(Path(unwatched_file).resolve()), True) in events


def test_touch(unwatched_file):
    events = run_command(["touch", str(unwatched_file)])
    assert FileEvent(str(Path(unwatched_file).resolve()), False) in events


def test_stat(unwatched_file):
    events = run_command(["stat", "-L", str(unwatched_file)])
    assert FileEvent(str(Path(unwatched_file).resolve()), True) in events


def test_lstat(unwatched_file):
    events = run_command(["stat", str(unwatched_file)])
    assert FileEvent(str(Path(unwatched_file).resolve()), True) in events


def test_unlink(unwatched_file):
    events = run_command(["unlink", str(unwatched_file)])
    assert FileEvent(str(Path(unwatched_file).resolve()), False) in events


def test_rm_r(tmp_path, unwatched_file):
    events = run_command(["rm", "-r", str(tmp_path)])
    assert FileEvent(str(Path(unwatched_file).resolve()), False) in events
