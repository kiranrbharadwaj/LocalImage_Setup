# Contributing

Use a branch and pull request. Describe the behavior changed and checks performed. Keep model weights, private reference images, outputs, tokens and machine-specific paths out of commits.

Run `python3.14 -m unittest discover -s tests -v`. For workflow changes, also validate against the pinned ComfyUI node schemas and, when possible, run a synthetic local inference test. Report hardware, versions, resolution, seed, steps and adapter strengths. Mark untested configurations clearly.

Do not make cloud services, broad network permissions, custom plugins or OS memory/security changes part of the default setup without explaining and reviewing their impact. Keep personal data out of issue attachments.
