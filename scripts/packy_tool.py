"""Acquire and invoke only the reviewed Packy release; no global installation."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

PLATFORMS = {"darwin_amd64", "darwin_arm64", "linux_amd64", "linux_arm64"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate release declaration key: " + key)
        result[key] = value
    return result


def read_pin(path):
    pin = json.loads(path.read_text(), object_pairs_hook=unique_object)
    if not isinstance(pin, dict) or set(pin) != {"version", "source_commit", "artifacts"}:
        raise ValueError("malformed release declaration: expected version, source_commit, artifacts")
    if not isinstance(pin["version"], str) or not re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", pin["version"]):
        raise ValueError("malformed release version: expected exact stable vMAJOR.MINOR.PATCH")
    if not isinstance(pin["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", pin["source_commit"]):
        raise ValueError("malformed release source commit: expected full lowercase SHA")
    artifacts = pin["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != PLATFORMS or any(
        not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest) for digest in artifacts.values()
    ):
        raise ValueError("malformed release artifacts: expected all four platform SHA-256 checksums")
    return pin


def platform_key():
    system = subprocess.check_output(["uname", "-s"], text=True).strip().lower()
    machine = subprocess.check_output(["uname", "-m"], text=True).strip()
    machine = {"x86_64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine, machine)
    key = system + "_" + machine
    if key not in PLATFORMS:
        raise ValueError("unsupported Packy platform: " + key)
    return key


def verify_archive(archive, digest, executable, pin):
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("partial or unsafe Packy cache entry: " + str(archive.parent) + "; remove it and retry")
    sealed = archive.read_bytes()
    if hashlib.sha256(sealed).hexdigest() != digest:
        raise ValueError("Packy archive checksum mismatch: " + str(archive.parent) + "; remove it and retry")
    with tarfile.open(fileobj=io.BytesIO(sealed), mode="r:gz") as bundle:
        members = bundle.getmembers()
        if len(members) != 1 or members[0].name != "packy" or not members[0].isfile() or members[0].size > 150_000_000:
            raise ValueError("invalid Packy archive: expected only the regular packy executable")
        with bundle.extractfile(members[0]) as source, executable.open("xb") as target:
            shutil.copyfileobj(source, target)
    executable.chmod(0o700)
    result = subprocess.run([str(executable), "version", "--json"], capture_output=True, text=True, timeout=15)
    expected = {"schema_version": 1, "report": "packy-version", "version": pin["version"],
                "source_commit": pin["source_commit"]}
    if result.returncode or json.loads(result.stdout) != expected:
        raise ValueError("Packy embedded identity mismatch with reviewed release declaration")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", type=Path, required=True)
    parser.add_argument("--executable-output", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not args.executable_output and not command:
        parser.error("a Packy command is required after --")
    pin = read_pin(args.pin)
    platform = platform_key()
    digest = pin["artifacts"][platform]
    cache_root = Path(os.environ.get("PACKY_CACHE_DIR") or (
        Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "packy-catalog" / "tooling"))
    cache_root.mkdir(parents=True, exist_ok=True)
    entry = cache_root / (pin["version"] + "-" + pin["source_commit"] + "-" + platform + "-" + digest)
    archive = entry / "release.tar.gz"
    with tempfile.TemporaryDirectory(prefix="packy-verified-") as scratch:
        executable = Path(scratch) / "packy"
        if entry.exists() or entry.is_symlink():
            if entry.is_symlink() or not entry.is_dir() or set(p.name for p in entry.iterdir()) != {"release.tar.gz"}:
                raise ValueError("partial or unsafe Packy cache entry: " + str(entry))
            verify_archive(archive, digest, executable, pin)
        else:
            with tempfile.TemporaryDirectory(prefix=".acquiring-", dir=cache_root) as staging:
                staged_archive = Path(staging) / "release.tar.gz"
                name = "packy_" + pin["version"] + "_" + platform + ".tar.gz"
                url = "https://github.com/yersonargotev/packy/releases/download/" + pin["version"] + "/" + name
                subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location", "--proto", "=https",
                                "--proto-redir", "=https", "--connect-timeout", "15", "--max-time", "120",
                                "--output", str(staged_archive), url], check=True)
                verify_archive(staged_archive, digest, executable, pin)
                # Atomically expose only a complete archive after checksum and identity verification.
                try:
                    os.rename(staging, entry)
                except FileExistsError:
                    raise ValueError("concurrent Packy acquisition; retry using the verified cache")
        if args.executable_output:
            # Used only by trusted inline workflow orchestration in the credentialed job.
            with args.executable_output.open("xb") as target, executable.open("rb") as source:
                shutil.copyfileobj(source, target)
            args.executable_output.chmod(0o700)
            return 0
        return subprocess.run([str(executable), *command]).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
        print("Packy tooling: " + str(error), file=sys.stderr)
        sys.exit(1)
