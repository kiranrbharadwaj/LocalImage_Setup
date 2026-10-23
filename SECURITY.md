# Security

Report security concerns privately through GitHub's vulnerability reporting feature if enabled, or contact the maintainer through their GitHub profile before posting sensitive details. Do not attach tokens, personal images or unsanitized logs to public issues.

Downloaded model files are checked against pinned sizes and SHA-256 hashes. Hashes establish that bytes match the selected publisher's file; they do not establish that a publisher or model is trustworthy. Safetensors weights are used rather than pickle checkpoints. The launcher disables custom/partner nodes and restricts network access to loopback for its process.

The local server has no user authentication and must remain bound to localhost. Do not expose it through LAN binding, reverse proxies or tunnels. Local processes and browser extensions may still have access; shared or hostile machines require a separate security design.

Dependencies and ComfyUI are pinned for reproducibility, not maintained automatically. Review security updates before refreshing the lock and rerun local checks. Do not run this setup on sensitive production systems.
