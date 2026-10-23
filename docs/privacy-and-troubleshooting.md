# Privacy and troubleshooting

## Controls provided

- Bound to `127.0.0.1:8188`; no LAN sharing or tunnel.
- `sandbox-exec` profile denies network access except localhost connections for the ComfyUI process and its descendants. This is a process restriction, not a global firewall change.
- `--offline` sets frontend restrictions and disables partner/cloud nodes.
- `--disable-all-custom-nodes` avoids extra executable plugins.
- Hugging Face offline/telemetry flags are set; PNG prompt metadata is disabled.

The installation phase needs network access to fetch source, packages and weights. It does not need user photos. This workflow runs no cloud model and needs no API key. The browser has its own permissions and networking environment; avoid untrusted extensions and do not infer a whole-machine privacy guarantee from the server sandbox.

Apple's `sandbox-exec` is a deprecated platform tool. It worked on macOS 26.7.1 in this trial; its availability and future behavior are not guaranteed. If it fails, the launcher fails rather than silently starting unrestricted. Do not remove the sandbox or add networking permissions just to bypass a startup error.

## Blank canvas / wrong graph

**Unsaved Workflow** is often ComfyUI's default generator or a blank tab. Open the **Workflows** sidebar (connected-boxes icon below Model Library), refresh, and double-click a supplied workflow. The panel heading must say Workflows. Loading a LoRA from Model Library only adds a node—it does not load the whole editing pipeline.

Close the sidebar, focus the canvas and use **Fit View** / `.`. The editing graph must contain **Load Image** and **Text Encode Qwen Image 2.1**, not only ordinary CLIP text encoders. Do not change CLIP's type from `qwen_image` to `lumina2` or add an AuraFlow sampling shift from a different tutorial.

## Heavy swapping or slow loading

Unload idle LM Studio models first. Use the launcher's tested BF16 text encoder, disk-backed loading and disabled intermediate caching. Our initial default loading attempt incurred about 4.35 GiB of new swap-outs before interruption. The revised settings completed the documented tests.

Begin with resolution 512 and one image. Two references, larger images and LoRA patching can increase peak memory. ComfyUI's CPU offload does not provide a separate RAM pool on a unified-memory Mac. Do not raise OS GPU memory limits or disable security protections to force a model to fit.

Use `memory_pressure -Q` and repeated `vm_stat` samples. Existing `vm.swapusage` is cumulative occupancy; it does not by itself show current swapping. In the trial, the first full-stack success recorded about 467 MiB new swap-outs; later successes recorded zero.

`scripts/smoke_test.py` monitors new swap-outs and requests interruption after 1 GiB or 20 minutes. A single allocation may overshoot between samples, and interruption may not take effect until a model operation returns. If the app remains busy or memory pressure persists after interruption, stop ComfyUI with Control-C in its launch terminal. The script does not kill unrelated processes, clear system swap, or change global memory limits. GUI Run requests have no automatic guard.

## Offline download / checksum failures

The launcher intentionally cannot fetch missing weights online. Stop it, run the model downloader during setup, and relaunch. The downloader checks SHA-256 plus size against the pinned manifest; an invalid final file is not silently overwritten. Review and move it aside, then retry. If a partial file repeatedly fails verification, remove only that model's `.part` file and retry. Do not download arbitrary similarly named checkpoints.

The dependency lock targets macOS arm64 / Python 3.14. If package wheels are unavailable, preserve the error and report it rather than silently substituting a different runtime. No Linux/Windows inference support is claimed by this repository.

## Image changed more than requested

Use one concrete instruction, compare base versus Consistency, and inspect non-target regions. The three-LoRA stack is not a universal quality upgrade. For difficult local edits, mask-guided conditioning or compositing may be needed; those paths require separate validation. Raising resolution does not guarantee better instruction following.

## Storage and removal

Source and dependencies: `.runtime/ComfyUI`; models: `.runtime/ComfyUI/models`; photos: `.runtime/ComfyUI/input`; results: `.runtime/ComfyUI/output`. These are Git-ignored but not encrypted by this project. Save private backups as appropriate.

To remove the setup, stop the server, preserve any wanted input/output/reference files, then remove the dedicated `.runtime` directory and clone. Do not remove shared Python installations, shared caches or LM Studio model files. No background service or startup login item is installed.
