#!/usr/bin/env python3
"""Create local secrets, then start this self-contained Docker Compose demo."""

import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "demo.json").read_text(encoding="utf-8"))


def prepare_env() -> None:
    target = ROOT / ".env"
    if target.exists():
        if "CHANGE_ME" in target.read_text(encoding="utf-8"):
            raise RuntimeError(".env still contains CHANGE_ME; fill it or remove it to regenerate")
        print("Using existing .env; persistent secrets are unchanged.")
        return
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in CONFIG["secret_keys"]:
        placeholder = f"{key}=CHANGE_ME"
        if content.count(placeholder) != 1:
            raise RuntimeError(f"Missing placeholder for {key}")
        content = content.replace(placeholder, f"{key}={secrets.token_hex(32)}")
    target.write_text(content, encoding="utf-8")
    os.chmod(target, 0o600)
    print("Created .env with fresh local secrets (mode 0600).")


def compose(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", "compose", *args], cwd=ROOT, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the project demo")
    parser.add_argument("--prepare-only", action="store_true", help="generate .env without starting containers")
    args = parser.parse_args()
    try:
        prepare_env()
        if args.prepare_only:
            return 0
        if not shutil.which("docker"):
            raise RuntimeError("Docker Compose v2+ is required; install Docker Desktop or Docker Engine + Compose")
        compose("version")
        compose("config", "-q")
        compose("pull")
        compose("up", "-d")
        model = CONFIG.get("ollama_model")
        if model:
            for _ in range(30):
                ready = compose("exec", "-T", "ollama", "ollama", "list", check=False)
                if ready.returncode == 0:
                    break
                time.sleep(2)
            else:
                raise RuntimeError("Ollama did not become ready; inspect docker compose logs ollama")
            compose("exec", "-T", "ollama", "ollama", "pull", model)
        env = dict(line.split("=", 1) for line in (ROOT / ".env").read_text().splitlines()
                   if line and not line.startswith("#") and "=" in line)
        port = env.get("DEMO_PORT", CONFIG["default_port"])
        print(f"Open http://127.0.0.1:{port} and follow README.md for the first-use path.")
        print("Run python3 verify.py to check HTTP readiness.")
        return 0
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Start failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
