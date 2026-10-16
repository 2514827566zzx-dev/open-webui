#!/usr/bin/env python3
"""Check the local HTTP entry point after Docker Compose has started."""

import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "demo.json").read_text(encoding="utf-8"))


def main() -> int:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("Run python3 start.py first.", file=sys.stderr)
        return 1
    env = dict(line.split("=", 1) for line in env_path.read_text().splitlines()
               if line and not line.startswith("#") and "=" in line)
    port = env.get("DEMO_PORT", CONFIG["default_port"])
    url = f"http://127.0.0.1:{port}{CONFIG['health_path']}"
    try:
        with urlopen(Request(url, headers={"User-Agent": "VirtueZ-Demo-Check/1.0"}), timeout=12) as response:
            body = response.read(20000).decode("utf-8", errors="replace")
            expected = CONFIG.get("health_contains")
            if expected and expected not in body:
                print(f"HTTP {response.status}, but expected marker {expected!r} was absent: {url}", file=sys.stderr)
                return 1
            print(f"HTTP {response.status}: {url}")
            return 0
    except (HTTPError, URLError) as error:
        print(f"HTTP check failed for {url}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
