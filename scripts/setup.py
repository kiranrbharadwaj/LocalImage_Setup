#!/usr/bin/env python3
"""Prepare a dedicated ComfyUI checkout/environment; model downloads are separate."""
import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
COMFY_COMMIT = "bc5f880dbdd43e426077f42ccec53bb577ffee9f"


def run(*args, **kwargs):
    subprocess.run(list(map(str, args)), check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable, help="Python 3.14 executable (tested with 3.14.8)")
    args = parser.parse_args()
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise SystemExit("This tested setup targets Apple Silicon macOS only.")
    version = json.loads(subprocess.check_output([args.python, "-c", "import sys,json;print(json.dumps(list(sys.version_info[:2])))"], text=True))
    if version != [3, 14]:
        raise SystemExit("Use Python 3.14 for this dependency lock. Other versions are untested.")
    if shutil.disk_usage(REPO).free < 8 * 1024**3:
        raise SystemExit("Need at least 8 GiB free for the runtime, in addition to model storage.")
    checkout = REPO / ".runtime/ComfyUI"
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--no-checkout", "https://github.com/Comfy-Org/ComfyUI.git", checkout)
        run("git", "-C", checkout, "checkout", "--detach", COMFY_COMMIT)
    head = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if head != COMFY_COMMIT:
        raise SystemExit("Existing ComfyUI checkout has a different revision; it has not been changed.")
    if subprocess.check_output(["git", "-C", str(checkout), "diff", "--name-only", "HEAD"], text=True).strip():
        raise SystemExit("Existing ComfyUI checkout has tracked edits; review them before installation.")
    python = checkout / ".venv/bin/python"
    if not python.exists():
        run(args.python, "-m", "venv", checkout / ".venv")
    run(python, "-m", "pip", "install", "-r", REPO / "requirements-macos-py314.lock")
    run(python, "-m", "pip", "check")
    destination = checkout / "user/default/workflows"
    destination.mkdir(parents=True, exist_ok=True)
    for source in (REPO / "workflows").glob("*-workflow.json"):
        target = destination / source.name
        if not target.exists():
            shutil.copy2(source, target)
    (checkout / "input").mkdir(parents=True, exist_ok=True)
    for source in (REPO / "examples").glob("*.png"):
        target = checkout / "input" / source.name
        if not target.exists():
            shutil.copy2(source, target)
    print("Runtime prepared. Review model licenses, download models, then run ./Start-ComfyUI.command")


if __name__ == "__main__":
    main()

