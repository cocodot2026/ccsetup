# ccsetup

**Configure Claude Code to use any Anthropic-compatible relay — and smoke-test it —
in one command. Zero dependencies. Your token is never stored or logged.**

Claude Code reads `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` (+ optional model
split). The two things people get wrong: the exact env vars, and whether the
endpoint actually answers. ccsetup does both — and tries the common auth-header and
path variants so relay quirks don't stump you.

## Use
```bash
python ccsetup.py --base-url https://<relay>/api/ai --token <key> --model <big-id>
python ccsetup.py --base-url ... --token ... --model <big> --small-model <small>
python ccsetup.py ... --write     # append the export block to your shell rc
python ccsetup.py ... --no-test   # just emit config, skip the smoke test
```

It will:
1. Smoke-test the endpoint against the Anthropic Messages API (across `x-api-key`
   vs `Bearer`, and `/v1/messages` vs `/messages`).
2. Print the exact `export` block to paste (or write it with `--write`).
3. Point you at the next step: verify no downgrade.

Sample:
```
[✓] endpoint answers the Anthropic Messages API · path=/v1/messages auth=Bearer model=... reply='pong'

Add this to your shell (~/.zshrc or ~/.bashrc):
# --- Claude Code relay config (ccsetup) ---
export ANTHROPIC_BASE_URL="https://<relay>/api/ai"
export ANTHROPIC_AUTH_TOKEN="<key>"
export ANTHROPIC_MODEL="<big-id>"
export ANTHROPIC_SMALL_FAST_MODEL="<small-id>"
# --- end ccsetup ---
```

## Where it fits
Part of a small honest toolkit for running AI from China:
[ccsetup](https://github.com/cocodot2026/ccsetup) (wire up Claude Code) ·
[relay-doctor](https://github.com/cocodot2026/relay-doctor) (is it alive?) ·
[LLMprobe](https://github.com/cocodot2026/LLMprobe) (real model?) ·
[ai-api-cost](https://github.com/cocodot2026/ai-api-cost) (cost) ·
[ai-coding-from-china](https://github.com/cocodot2026/ai-coding-from-china) (the full skill).

The author builds [cocodot](https://cocodot.co), a relay — disclosed; this tool
works against any Anthropic-compatible endpoint. MIT.
