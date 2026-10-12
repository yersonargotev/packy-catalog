"""Checked fixture preparation; ordinary tests observe failures at their public runner."""
import math
import os
import re

from scripts.probes.content_probe_process import ChildDeadlineExpired, run_child


def prepare(command, *, label, cwd=None, env=None, timeout=30, redact=()):
    """Return captured stdout, or fail with the fixture command's diagnostic."""
    env = os.environ if env is None else env
    secrets = set(redact)
    secrets.update(value for key, value in env.items()
                   if re.search(r"TOKEN|PASSWORD|SECRET|CREDENTIAL|(?:^|_)KEY(?:$|_)", key, re.I))

    def fail(message):
        diagnostic = f"fixture command {label}: {message}"
        for value in sorted(filter(None, secrets), key=len, reverse=True):
            diagnostic = diagnostic.replace(value, "[redacted]")
        if len(diagnostic) > 8192:
            diagnostic = diagnostic[:8192] + "\n[diagnostic truncated]"
        raise RuntimeError(diagnostic) from None

    if not math.isfinite(timeout) or timeout <= 0:
        fail("deadline must be finite and positive")
    try:
        status, stdout, stderr = run_child(command, cwd=cwd, env=env, timeout=timeout, check_approval=False)
    except ChildDeadlineExpired as error:
        fail(f"deadline expired after {timeout}s\n{error.stderr}")
    except OSError as error:
        fail(f"execution failed (errno {error.errno}: {error.strerror})")
    except RuntimeError as error:
        fail(str(error))
    if status:
        fail(f"exit status {status}\n{stderr}")
    return stdout
