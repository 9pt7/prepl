import subprocess
import os
import socket
import tempfile
import json
import threading
from pathlib import Path
from collections import namedtuple


def _target(cmd, addr):

    env = os.environ.copy()
    env["PWATCH_SOCK"] = addr
    ld_preload_parts = [str(Path(__file__).parent.absolute() / "libpwatch.so")]
    try:
        ld_preload_parts.append(env["LD_PRELOAD"])
    except KeyError:
        pass
    env["LD_PRELOAD"] = " ".join(ld_preload_parts)

    proc = subprocess.Popen(cmd, env=env)
    returncode = proc.wait()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0) as s:
        s.connect(addr)
        msg = {"kind": "finish", "returncode": returncode}
        s.send((json.dumps(msg) + "\n").encode("utf8"))


FileEvent = namedtuple("FileEvent", ("path", "readonly"))


def run_command(cmd, event_handler):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0) as sock:
        addr = tempfile.mktemp(suffix=".sock", prefix="pwatch-")
        sock.bind(addr)
        try:
            sock.listen()

            thread = threading.Thread(target=_target, args=(cmd, addr))
            thread.start()

            while True:
                conn, sockaddr = sock.accept()
                try:
                    with os.fdopen(conn.fileno(), "r", closefd=False) as f:
                        msg = json.loads(f.readline())

                    if msg["kind"] == "finish":
                        rc = msg["returncode"]
                        if rc != 0:
                            raise subprocess.CalledProcessError(rc, " ".join(cmd))
                        break
                    elif msg["kind"] == "openfile":
                        try:
                            evt = FileEvent(Path(msg["path"]), msg["readonly"])
                            event_handler(evt)
                        finally:
                            conn.send(b"\n")
                finally:
                    conn.close()
        finally:
            os.unlink(addr)
