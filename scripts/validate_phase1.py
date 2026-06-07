from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    paths = ["web_core_reference", "app", "tests", "scripts/smoke_api.py"]
    for path in paths:
        if not compileall.compile_file(ROOT / path, quiet=1) if Path(path).suffix == ".py" else not compileall.compile_dir(ROOT / path, quiet=1):
            raise SystemExit(1)
    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "scripts/smoke_api.py"])


if __name__ == "__main__":
    main()