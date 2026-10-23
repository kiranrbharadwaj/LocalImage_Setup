#!/usr/bin/env python3
"""Run one synthetic workflow against an idle local ComfyUI with bounded monitoring."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.request

REPO = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8188"


def request(path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    return json.loads(raw) if raw else {}


def swap_written():
    raw = subprocess.check_output(["vm_stat"], text=True)
    page = int(re.search(r"page size of (\d+) bytes", raw).group(1))
    count = int(re.search(r"Swapouts:\s+(\d+)", raw).group(1))
    return page * count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", choices=["base", "consistency", "three-loras"], default="consistency")
    args = parser.parse_args()
    queue = request("/queue")
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise SystemExit("ComfyUI is busy. Wait for existing work to finish.")
    baseline = swap_written()
    prompt = json.loads((REPO / "workflows" / (args.workflow + "-api.json")).read_text())
    result = request("/prompt", {"prompt": prompt})
    prompt_id = result["prompt_id"]
    start = time.monotonic()
    report = {"prompt_id": prompt_id, "workflow": args.workflow}
    try:
        while True:
            history = request("/history/" + prompt_id).get(prompt_id)
            elapsed = time.monotonic() - start
            additional = max(0, swap_written() - baseline)
            report.update(elapsed_seconds=round(elapsed, 2), additional_swap_bytes=additional)
            if history:
                report["status"] = history.get("status", {})
                report["outputs"] = history.get("outputs", {})
                if history.get("status", {}).get("status_str") != "success":
                    raise RuntimeError("Workflow failed; inspect the saved report and ComfyUI console")
                print("Completed:", json.dumps(report, indent=2))
                break
            if elapsed > 1200 or additional > 1024**3:
                raise RuntimeError("Stopped: exceeded 20 minutes or 1 GiB of additional swap")
            time.sleep(2)
    except BaseException as error:
        report["error"] = str(error)
        # Target only this request; never globally interrupt somebody else's work.
        request("/interrupt", {"prompt_id": prompt_id})
        request("/queue", {"delete": [prompt_id]})
        raise
    finally:
        folder = REPO / "results"
        folder.mkdir(exist_ok=True)
        (folder / (prompt_id + ".json")).write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
