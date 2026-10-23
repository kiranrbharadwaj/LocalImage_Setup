#!/usr/bin/env python3
"""Download only pinned model files; verify content before making it available."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import urllib.parse

REPO = Path(__file__).resolve().parents[1]


def manifest():
    data = json.loads((REPO / "models.json").read_text())
    for item in data:
        path = PurePosixPath(item["path"])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe destination path")
        if len(item["revision"]) != 40 or len(item["sha256"]) != 64:
            raise ValueError("Unpinned model")
        int(item["revision"], 16)
        int(item["sha256"], 16)
    return data


def verify(path, item):
    if not path.is_file() or path.stat().st_size != item["size"]:
        return False
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(16 * 1024**2), b""):
            h.update(block)
    return h.hexdigest() == item["sha256"]


def install(root, include_character=False, verify_only=False):
    selected = [x for x in manifest() if include_character or x["group"] != "character"]
    required = sum(x["size"] for x in selected if not (root / x["path"]).exists())
    if not verify_only:
        root.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(root).free < required + 8 * 1024**3:
            raise RuntimeError("Insufficient free disk space for selected models plus 8 GiB reserve")
    for item in selected:
        target = root / item["path"]
        if verify(target, item):
            print("Verified:", item["path"], flush=True)
            continue
        if verify_only:
            raise RuntimeError("Missing or invalid model: " + item["path"])
        if target.exists():
            raise RuntimeError("Existing model failed verification; move it aside before retrying: " + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        part = target.with_name(target.name + ".part")
        url = "https://huggingface.co/" + item["repo"] + "/resolve/" + item["revision"] + "/" + urllib.parse.quote(item["source_path"], safe="/")
        subprocess.run(["curl", "--location", "--fail", "--retry", "3", "--continue-at", "-", "--output", str(part), url], check=True)
        if not verify(part, item):
            raise RuntimeError("Downloaded file failed SHA-256/size check; partial file retained: " + str(part))
        part.rename(target)
        print("Downloaded and verified:", item["path"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / ".runtime/ComfyUI/models")
    parser.add_argument("--include-character-loras", action="store_true", help="Also download Anything2Real and the NSFW-labeled TheseAlpacas V2 adapter")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        print(json.dumps(manifest(), indent=2))
        return
    install(args.root.resolve(), args.include_character_loras, args.verify_only)


if __name__ == "__main__":
    main()

