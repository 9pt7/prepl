import subprocess
import os
import tempfile
import json
import threading
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager


@contextmanager
def _fifo():

    dirpath = tempfile.mkdtemp(prefix="pwatch-")
    try:
        fifo_path = Path(dirpath) / "fifo"
        os.mkfifo(fifo_path)
        try:
            fd = os.open(fifo_path, os.O_RDWR)
            try:
                fifo = os.fdopen(fd, "r", closefd=False)
                try:
                    yield fifo, fifo_path
                finally:
                    fifo.close()
            finally:
                os.close(fd)
        finally:
            os.unlink(fifo_path)
    finally:
        os.rmdir(dirpath)


def _target(cmd, fifo_path):

    env = os.environ.copy()
    env["PWATCH_FIFO"] = fifo_path
    ld_preload_parts = [str(Path(__file__).parent.absolute() / "libpwatch.so")]
    try:
        ld_preload_parts.append(env["LD_PRELOAD"])
    except KeyError:
        pass
    env["LD_PRELOAD"] = " ".join(ld_preload_parts)

    proc = subprocess.Popen(cmd, env=env)
    returncode = proc.wait()
    try:
        with open(fifo_path, "w") as fifo:
            msg = {"kind": "finish", "returncode": returncode}
            fifo.write(json.dumps(msg) + "\n")
    except FileNotFoundError:
        # The fifo must have already been closed
        pass


FileEvent = namedtuple("FileEvent", ("path", "readonly"))


def run_command(cmd, event_handler=None):

    if event_handler is None:
        events = []

        def event_handler(event):
            events.append(event)

    else:
        events = None

    with _fifo() as (fifo, fifo_path):
        thread = threading.Thread(target=_target, args=(cmd, fifo_path))
        thread.start()

        while True:
            msg = json.loads(fifo.readline())

            if msg["kind"] == "finish":
                rc = msg["returncode"]
                if rc != 0:
                    raise subprocess.CalledProcessError(rc, " ".join(cmd))
                break
            elif msg["kind"] == "openfile":
                evt = FileEvent(msg["path"], msg["readonly"])
                event_handler(evt)

    return events
