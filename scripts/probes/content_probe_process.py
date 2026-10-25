"""Bounded, isolated child execution with exact, single-use PTY approval."""
import json
import os
import pty
import selectors
import signal
import subprocess
import time


class ChildDeadlineExpired(RuntimeError):
    def __init__(self, output):
        super().__init__("child timeout: deadline expired")
        self.stderr = output["stderr"].decode(errors="replace")


class ChildSpawnFailed(RuntimeError):
    pass


def run_child(command, *, cwd, env, timeout, approval=None, check_approval=True):
    # None closes stdin; an explicit empty sequence requests a terminal with no approvals.
    master, slave = pty.openpty()
    child = None
    output = {"stdout": bytearray(), "stderr": bytearray()}
    prompts = [approval] if isinstance(approval, str) else list(approval or [])
    answered = 0
    try:
        try:
            child = subprocess.Popen(command, cwd=cwd, env=env, stdin=slave if approval is not None else subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        except OSError as error:
            raise ChildSpawnFailed(f"spawn failed (errno {error.errno}: {error.strerror})") from None
        os.close(slave)
        slave = None
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ, "stdout")
            selector.register(child.stderr, selectors.EVENT_READ, "stderr")
            while selector.get_map():
                if child.poll() is not None:
                    # Descendants must not keep pipes open after the command exits.
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if time.monotonic() >= deadline:
                    raise ChildDeadlineExpired(output)
                for key, _ in selector.select(min(0.1, max(0, deadline - time.monotonic()))):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    stream = output[key.data]
                    stream.extend(data)
                    if sum(len(value) for value in output.values()) > 16_000_000:
                        raise RuntimeError("child output exceeded limit")
                    if check_approval and b"[y/N]" in stream:
                        expected = prompts[answered].encode() if answered < len(prompts) else b""
                        prefix, separator, prompt = bytes(stream).rpartition(b"\n")
                        if key.data != "stdout" or not expected or not expected.startswith(prompt):
                            raise RuntimeError("unexpected child approval prompt: " + stream.decode(errors="replace"))
                        if prompt == expected:
                            for line in prefix.splitlines():
                                if not isinstance(json.loads(line), dict):
                                    raise RuntimeError("unstructured output before approval")
                            os.write(master, b"y\n")
                            answered += 1
                            stream.clear()
                            stream.extend(prefix + separator)
            try:
                status = child.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                raise ChildDeadlineExpired(output) from None
        if status == 0 and answered != len(prompts):
            raise RuntimeError("child succeeded without expected approval")
        return status, output["stdout"].decode(errors="replace"), output["stderr"].decode(errors="replace")
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
