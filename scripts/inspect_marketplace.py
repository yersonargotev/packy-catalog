"""Read-only, bounded inspection of observed Claude marketplace source forms."""
import argparse
import json
from pathlib import Path, PureWindowsPath
import stat
import sys


OUTPUT_BYTES = 16384
ENTRY_LIMIT = 20
PATH_LIMIT = 100
FIELD_BYTES = 512
MANIFEST = ".claude-plugin/marketplace.json"
CATEGORIES = ("local_present", "local_absent", "external", "unsupported", "malformed", "unsafe")


def evidence(value):
    """Keep original JSON syntax, explicitly labelling any incomplete preview."""
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    return {"json": encoded[:FIELD_BYTES], "truncated": len(encoded) > FIELD_BYTES}


def safe_path(root, relative):
    """Reject links component by component before any descendant is accessed."""
    windows = PureWindowsPath(relative)
    parts = relative.replace("\\", "/").split("/")
    if relative.startswith("/") or windows.drive or windows.root or ".." in parts or "\x00" in relative:
        raise ValueError("absolute, traversing, or invalid local path")
    current = root
    for part in parts:
        if part in ("", "."):
            continue
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise ValueError("symlink local path (links are not followed)")
    return current


def classify(root, entry):
    if not isinstance(entry, dict) or not isinstance(entry.get("name"), str) or not entry["name"].strip():
        return "malformed", "entry requires a nonempty string name"
    source = entry.get("source")
    if isinstance(source, str):
        if not source.strip():
            return "malformed", "empty local source"
        try:
            target = safe_path(root, source)
            if not target.exists():
                return "local_absent", "local source does not exist"
            if not target.is_dir():
                return "malformed", "local source is not a directory"
        except ValueError as error:
            return "unsafe", str(error)
        except OSError:
            return "malformed", "local source cannot be inspected"
        return "local_present", "local directory"
    if isinstance(source, dict):
        form = source.get("source")
        if not isinstance(form, str) or not form:
            return "malformed", "source object requires a string source discriminator"
        if form not in ("url", "git-subdir"):
            return "unsupported", "unrecognized source form"
        required = ("url", "path") if form == "git-subdir" else ("url",)
        if any(not isinstance(source.get(key), str) or not source[key].strip() for key in required):
            return "malformed", "external source missing required nonempty string fields"
        return "external", "external reference; not fetched"
    return "malformed", "source must be a relative string or source object"


def emit(report):
    """Bound the entire JSON document, including escaping and its final newline."""
    report["limits"] = {"output_bytes": OUTPUT_BYTES, "entries": ENTRY_LIMIT,
                        "paths": PATH_LIMIT, "field_json_bytes": FIELD_BYTES}
    while True:
        payload = json.dumps(report, ensure_ascii=True, separators=(",", ":")) + "\n"
        if len(payload.encode("utf-8")) <= OUTPUT_BYTES:
            sys.stdout.write(payload)
            return
        for key in ("inventory", "entries"):
            listing = report.get(key)
            if listing and listing["items"]:
                listing["items"].pop()
                listing["omitted"] += 1
                break
        else:
            # All remaining variable fields are bounded previews; this is a
            # defensive fallback if the fixed report structure ever grows.
            report = {"error": evidence("report exceeds output budget")}


def inventory(root, start):
    items = []
    total = 0
    pending = [start]
    while pending:
        directory = pending.pop()
        children = sorted(directory.iterdir(), key=lambda path: path.name)
        directories = []
        for child in children:
            mode = child.lstat().st_mode
            kind = "symlink" if stat.S_ISLNK(mode) else "directory" if stat.S_ISDIR(mode) else "file" if stat.S_ISREG(mode) else "special"
            total += 1
            if len(items) < PATH_LIMIT:
                items.append({"path": evidence(child.relative_to(root).as_posix()), "kind": kind})
            if kind == "directory":
                directories.append(child)
        pending.extend(reversed(directories))
    return {"root": evidence(start.relative_to(root).as_posix()), "total": total,
            "items": items, "omitted": total - len(items)}


def reject_constant(value):
    raise ValueError("nonstandard JSON constant: " + value)


def inspect(root, selected_name=None, include_inventory=False):
    manifest = safe_path(root, MANIFEST)
    if not manifest.is_file():
        raise ValueError("marketplace manifest is not a regular file")
    with manifest.open(encoding="utf-8") as stream:
        data = json.load(stream, parse_constant=reject_constant)
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
        raise ValueError("marketplace must be an object with a plugins array")
    counts = dict.fromkeys(CATEGORIES, 0)
    items = []
    for index, entry in enumerate(data["plugins"]):
        category, reason = classify(root, entry)
        counts[category] += 1
        if len(items) < ENTRY_LIMIT:
            items.append({"index": index, "name": evidence(entry.get("name") if isinstance(entry, dict) else None),
                          "classification": category, "reason": reason})
    report = {"manifest": MANIFEST, "metadata": evidence({key: value for key, value in data.items() if key != "plugins"}),
            "total_entries": len(data["plugins"]), "counts": counts,
            "entries": {"total": len(data["plugins"]), "items": items,
                        "omitted": len(data["plugins"]) - len(items)}}
    if selected_name is not None:
        matches = [(index, entry) for index, entry in enumerate(data["plugins"])
                   if isinstance(entry, dict) and entry.get("name") == selected_name]
        if not matches:
            raise ValueError("selected name not found")
        if len(matches) != 1:
            raise ValueError("selected name is ambiguous: duplicate entries")
        index, entry = matches[0]
        category, reason = classify(root, entry)
        report["selected"] = {"location": f"/plugins/{index}", "name": evidence(entry["name"]),
                              "source": evidence(entry.get("source")), "classification": category,
                              "reason": reason, "entry": evidence(entry)}
    if include_inventory:
        start = root
        if selected_name is not None:
            if category != "local_present":
                raise ValueError("selected inventory requires a present local directory")
            start = safe_path(root, entry["source"])
        report["inventory"] = inventory(root, start)
    return report


class BoundedParser(argparse.ArgumentParser):
    def error(self, message):
        emit({"error": evidence(message)})
        raise SystemExit(2)


def main():
    parser = BoundedParser(prog="inspect_marketplace.py", description=__doc__)
    parser.add_argument("checkout")
    parser.add_argument("--entry", help="exact plugin name (duplicates fail)")
    parser.add_argument("--inventory", action="store_true", help="list checkout paths, or selected local directory paths")
    args = parser.parse_args()
    try:
        root = Path(args.checkout).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("checkout is not a directory")
        emit(inspect(root, args.entry, args.inventory))
        return 0
    except (OSError, ValueError, RecursionError) as error:
        emit({"error": evidence(str(error))})
        return 1


if __name__ == "__main__":
    sys.exit(main())
