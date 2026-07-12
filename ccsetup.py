#!/usr/bin/env python3
"""
ccsetup — configure Claude Code to use any Anthropic-compatible relay, and smoke
test it, in one command. No dependencies (Python 3 stdlib only).

Claude Code reads ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN (+ optional model
split). The two things people get wrong are (a) the exact env vars and (b) whether
the endpoint actually answers. This does both:
  1. smoke-tests your endpoint against the Anthropic Messages API (tries the common
     auth-header + path variants so relay quirks don't stump you), then
  2. prints the exact export block to paste — or writes it to your shell profile
     with --write.

Your token is used only for the test call; never stored or logged by this tool.

Usage:
    python ccsetup.py --base-url https://<relay>/api/ai --token <key> --model <big-id>
    python ccsetup.py --base-url ... --token ... --model <big> --small-model <small>
    python ccsetup.py ... --write        # append the export block to your shell rc
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def try_messages(base, token, model):
    """Try Anthropic Messages API across common path + auth variants.
    Returns (ok, detail_str)."""
    body = json.dumps({
        "model": model, "max_tokens": 16,
        "messages": [{"role": "user", "content": "Reply with the single word: pong"}],
    }).encode()
    paths = ["/v1/messages", "/messages"]
    auth_variants = [
        {"x-api-key": token, "anthropic-version": "2023-06-01"},
        {"Authorization": f"Bearer {token}", "anthropic-version": "2023-06-01"},
    ]
    last = "no attempt"
    for path in paths:
        url = base.rstrip("/") + path
        for headers in auth_variants:
            try:
                req = urllib.request.Request(url, data=body, method="POST")
                req.add_header("Content-Type", "application/json")
                for k, v in headers.items():
                    req.add_header(k, v)
                resp = urllib.request.urlopen(req, timeout=60)
                data = json.loads(resp.read().decode())
                text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        text += block.get("text", "")
                auth_used = "x-api-key" if "x-api-key" in headers else "Bearer"
                return True, f"path={path} auth={auth_used} model={data.get('model','?')} reply={text.strip()[:30]!r}"
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code} at {path}"
            except Exception as e:
                last = f"{type(e).__name__} at {path}"
    return False, last


def export_block(base, token, model, small):
    lines = [
        "# --- Claude Code relay config (ccsetup) ---",
        f'export ANTHROPIC_BASE_URL="{base}"',
        f'export ANTHROPIC_AUTH_TOKEN="{token}"',
    ]
    if model:
        lines.append(f'export ANTHROPIC_MODEL="{model}"')
    if small:
        lines.append(f'export ANTHROPIC_SMALL_FAST_MODEL="{small}"')
    lines.append("# --- end ccsetup ---")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base-url", required=True, help="Anthropic-compatible base URL of the relay")
    p.add_argument("--token", required=True, help="your relay key")
    p.add_argument("--model", help="big/flagship model id (ANTHROPIC_MODEL)")
    p.add_argument("--small-model", help="small/fast model id (ANTHROPIC_SMALL_FAST_MODEL)")
    p.add_argument("--write", action="store_true", help="append the export block to your shell rc")
    p.add_argument("--no-test", action="store_true", help="skip the smoke test, just emit config")
    args = p.parse_args()

    print(f"ccsetup → {args.base_url}\n")

    if not args.no_test:
        test_model = args.model or "claude-3-5-sonnet"
        ok, detail = try_messages(args.base_url, args.token, test_model)
        if ok:
            print(f"[✓] endpoint answers the Anthropic Messages API · {detail}")
        else:
            print(f"[✗] smoke test failed · {detail}")
            print("    - check base URL, token, and that --model is an id THIS relay exposes")
            print("    - if this relay is OpenAI-only (not Anthropic-compatible), Claude Code")
            print("      won't work against it; use an Anthropic-compatible endpoint.")
            print("    - config still printed below so you can adjust and retry.\n")

    block = export_block(args.base_url, args.token, args.model, args.small_model)
    print("\nAdd this to your shell (~/.zshrc or ~/.bashrc), then restart your shell:\n")
    print(block)

    if args.write:
        rc = os.path.expanduser("~/.zshrc" if os.environ.get("SHELL", "").endswith("zsh")
                                else "~/.bashrc")
        with open(rc, "a", encoding="utf-8") as f:
            f.write("\n" + block + "\n")
        print(f"\n[written] appended to {rc} — run:  source {rc}")
    else:
        print("\n(tip: add --write to append this to your shell rc automatically)")

    print("\nThen just run:  claude")
    print("Next: verify you're getting the real model → LLMprobe "
          "(github.com/cocodot2026/cocodot-llmprobe).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
