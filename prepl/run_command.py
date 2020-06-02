import subprocess
import os
import tempfile
import json
import threading
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def _fifo():

    dirpath = tempfile.mkdtemp(prefix="prepl-")
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


def _target(proc, fifo_path):
    returncode = proc.wait()
    try:
        with open(fifo_path, "w") as fifo:
            msg = {"kind": "finish", "returncode": returncode}
            fifo.write(json.dumps(msg) + "\n")
    except FileNotFoundError:
        # The fifo must have already been closed
        pass


FileEvent = namedtuple("FileEvent", ("path", "readonly"))


def run_command(cmd, event_handler=None, shell=False):

    command_string = " ".join(str(part) for part in cmd) if type(cmd) == list else cmd

    logging.info(f"running command '{command_string}'")

    if event_handler is None:
        events = []

        def event_handler(event):
            events.append(event)

    else:
        events = None

    with _fifo() as (fifo, fifo_path):
        env = os.environ.copy()
        env["PREPL_FIFO"] = fifo_path
        ld_preload_parts = [str(Path(__file__).parent.absolute() / "libprepl.so")]
        try:
            ld_preload_parts.append(env["LD_PRELOAD"])
        except KeyError:
            pass
        env["LD_PRELOAD"] = " ".join(ld_preload_parts)

        proc = subprocess.Popen(cmd, env=env, shell=shell)

        thread = threading.Thread(target=_target, args=(proc, fifo_path))
        thread.start()

        while True:
            msg = json.loads(fifo.readline())

            if msg["kind"] == "finish":
                rc = msg["returncode"]

                if rc == 0:
                    logger.info(f"'{command_string}' finished successfully")
                else:
                    logger.info(f"'{command_string}' failed with exit status {rc}")
                break
            elif msg["kind"] == "openfile":
                evt = FileEvent(str(Path(msg["path"]).resolve()), msg["readonly"])
                logger.debug(f"access({'r' if evt.readonly else 'w'}): {evt.path}")
                event_handler(evt)

    return events
