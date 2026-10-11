"""Bounded, isolated child execution with exact, single-use PTY approval."""
import json
import os
import pty
import selectors
import signal
import subprocess
import time


def run_child(command, *, cwd, env, timeout, approval=None):
    master, slave = pty.openpty()
    child = None
    output = {"stdout": bytearray(), "stderr": bytearray()}
    answered = False
    try:
        child = subprocess.Popen(command, cwd=cwd, env=env, stdin=slave if approval else subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        os.close(slave)
        slave = None
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ, "stdout")
            selector.register(child.stderr, selectors.EVENT_READ, "stderr")
            while selector.get_map():
                if time.monotonic() >= deadline:
                    raise RuntimeError("child timeout: " + repr(command))
                for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    stream = output[key.data]
                    stream.extend(data)
                    if sum(len(value) for value in output.values()) > 16_000_000:
                        raise RuntimeError("child output exceeded limit")
                    if b"[y/N]" in stream:
                        expected = approval.encode() if approval else b""
                        prefix, separator, prompt = bytes(stream).rpartition(b"\n")
                        if key.data != "stdout" or answered or not expected or not expected.startswith(prompt):
                            raise RuntimeError("unexpected child approval prompt: " + stream.decode(errors="replace"))
                        if prompt == expected:
                            for line in prefix.splitlines():
                                if not isinstance(json.loads(line), dict):
                                    raise RuntimeError("unstructured output before approval")
                            os.write(master, b"y\n")
                            answered = True
                            stream.clear()
                            stream.extend(prefix + separator)
            status = child.wait(timeout=max(0.01, deadline - time.monotonic()))
        if approval and status == 0 and not answered:
            raise RuntimeError("child succeeded without expected approval")
        return status, output["stdout"].decode(), output["stderr"].decode()
    finally:
        if child is not None:
            # Kill the owned process group even when its leader already exited.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            child.stdout.close()
            child.stderr.close()
        if slave is not None:
            os.close(slave)
        os.close(master)
