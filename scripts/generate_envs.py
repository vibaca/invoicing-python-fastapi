#!/usr/bin/env python3
"""Genera `.env` y `.env.test` a partir de `.env.example`.

Uso:
    python scripts/generate_envs.py
    python scripts/generate_envs.py --example .env.example --out .env --out-test .env.test

Reglas básicas:
- `.env` toma la versión por defecto del ejemplo (preserva valores comentados).
- `.env.test` aplica cambios útiles para test: `APP_ENV=test`, `APP_DEBUG=false`,
  `TEST_MODE=1`, y sustituye coincidencias de `_dev` en `DB_NAME` y `DATABASE_URL`
  por `_test` cuando corresponda.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_env_lines(lines: list[str]) -> list[tuple[str|None,str]]:
    """Parses lines into (key, line) where key is None for non key=value lines."""
    parsed = []
    for ln in lines:
        m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", ln)
        if m:
            parsed.append((m.group(1), ln))
        else:
            parsed.append((None, ln))
    return parsed


def write_env(base_lines: list[str], out_path: Path, overrides: dict[str,str]) -> None:
    parsed = parse_env_lines(base_lines)
    with out_path.open("w", encoding="utf-8") as f:
        for key, line in parsed:
            if key is None:
                f.write(line)
                continue

            if key in overrides:
                f.write(f"{key}={overrides[key]}\n")
            else:
                f.write(line)


def make_test_overrides(lines: list[str]) -> dict[str,str]:
    # Defaults for test
    overrides: dict[str,str] = {
        "APP_ENV": "test",
        "APP_DEBUG": "false",
        "TEST_MODE": "1",
    }

    # Try to detect DB_NAME and DATABASE_URL from example to rewrite to test variants
    db_name = None
    db_url = None
    for ln in lines:
        m = re.match(r"\s*DB_NAME\s*=\s*(.+)", ln)
        if m:
            db_name = m.group(1).strip()
        m2 = re.match(r"\s*DATABASE_URL\s*=\s*(.+)", ln)
        if m2:
            db_url = m2.group(1).strip()

    if db_name:
        if db_name.endswith("_dev"):
            overrides["DB_NAME"] = db_name[:-4] + "_test"
        else:
            overrides.setdefault("DB_NAME", db_name + "_test")

    if db_url:
        # Basic replacement of _dev -> _test in the URL if present
        if "_dev" in db_url:
            overrides["DATABASE_URL"] = db_url.replace("_dev", "_test")
        else:
            # If no _dev, try to replace the last path segment with test variant
            m = re.match(r"(.+)/(\w+)(\W*)$", db_url)
            if m:
                prefix, name, suffix = m.groups()
                overrides["DATABASE_URL"] = f"{prefix}/{name}_test{suffix}"

    return overrides


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--example", default=".env.example", help="Path to .env.example")
    p.add_argument("--out", default=".env", help="Output .env path for dev")
    p.add_argument("--out-test", default=".env.test", help="Output .env.test path for tests")
    args = p.parse_args()

    example = Path(args.example)
    if not example.exists():
        print(f"No existe {example}. Crea primero .env.example")
        raise SystemExit(1)

    base_lines = example.read_text(encoding="utf-8").splitlines(keepends=True)

    # Write dev .env (keep values from example, but ensure TEST_MODE=0 if present)
    dev_overrides = {"TEST_MODE": "0"}
    write_env(base_lines, Path(args.out), dev_overrides)

    # Generate test overrides
    test_overrides = make_test_overrides(base_lines)
    write_env(base_lines, Path(args.out_test), test_overrides)

    print(f"Generados: {args.out} y {args.out_test}")


if __name__ == "__main__":
    main()
