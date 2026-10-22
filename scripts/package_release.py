#!/usr/bin/env python3
"""Validate Botile metadata and package a tagged release.

This script never creates or moves a Git tag. It refuses to package unless the
requested tag already exists and points at the checked-out commit.

Usage:
    python3 scripts/package_release.py --check
    python3 scripts/package_release.py --tag v1.1.3 --output-dir dist
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "Botile.plugin"
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
META_NAMES = {
    "__id__",
    "__name__",
    "__version__",
    "__app_version__",
    "__sdk_version__",
    "__permissions__",
}


def fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def read_metadata(path: Path) -> dict[str, object]:
    if not path.is_file():
        fail(f"plugin file not found: {path}")

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as error:
        fail(f"cannot parse {path}: {error}")

    metadata: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in META_NAMES:
            continue
        if target.id in metadata:
            fail(f"duplicate top-level metadata assignment: {target.id}")
        try:
            metadata[target.id] = ast.literal_eval(node.value)
        except (TypeError, ValueError) as error:
            fail(f"metadata {target.id} must be a literal: {error}")

    missing = sorted(META_NAMES - metadata.keys())
    if missing:
        fail("missing top-level metadata: " + ", ".join(missing))

    version = metadata["__version__"]
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        fail("__version__ must be a strict MAJOR.MINOR.PATCH version")

    for key in ("__app_version__", "__sdk_version__"):
        value = metadata[key]
        if not isinstance(value, str) or not value.strip():
            fail(f"{key} must be a non-empty string")

    permissions = metadata["__permissions__"]
    if not isinstance(permissions, (list, tuple)) or not all(
        isinstance(item, str) for item in permissions
    ):
        fail("__permissions__ must be a list of strings")
    if "hooks" not in permissions:
        fail("__permissions__ must declare the hooks permission")

    if metadata["__id__"] != "botile":
        fail("__id__ must remain botile")

    return metadata


def tag_version(tag: str) -> str:
    match = TAG_RE.fullmatch(tag)
    if not match:
        fail(f"tag must be strict vMAJOR.MINOR.PATCH, got: {tag}")
    return ".".join(match.groups())


def git(*args: str, allow_missing: bool = False) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        if allow_missing:
            return None
        fail(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def require_existing_tag(tag: str) -> None:
    tag_ref = f"refs/tags/{tag}^{{commit}}"
    tag_commit = git("rev-parse", "--verify", tag_ref, allow_missing=True)
    if not tag_commit:
        fail(
            f"tag {tag} does not exist locally; create and review it manually "
            "before packaging (this script never creates tags)"
        )

    head = git("rev-parse", "HEAD")
    if head != tag_commit:
        fail(
            f"HEAD {head} is not the commit for tag {tag} ({tag_commit}); "
            "check out the reviewed tag before packaging"
        )


def require_clean_worktree() -> None:
    status = git("status", "--porcelain", "--untracked-files=all")
    if status:
        fail(
            "working tree is not clean; commit or stash changes before packaging "
            "a release"
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def package(version: str, output_dir: Path) -> None:
    require_clean_worktree()
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_name = f"Botile-{version}.plugin"
    destination = output_dir / asset_name
    source_digest = sha256(PLUGIN)
    shutil.copyfile(PLUGIN, destination)
    destination_digest = sha256(destination)
    if source_digest != destination_digest:
        fail("packaged asset does not match Botile.plugin byte-for-byte")

    checksums = output_dir / "SHA256SUMS"
    with checksums.open("w", encoding="ascii", newline="\n") as output:
        output.write(f"{destination_digest}  {asset_name}\n")

    print(f"version={version}")
    print(f"asset={display_path(destination)}")
    print(f"sha256={destination_digest}")
    print(f"checksums={display_path(checksums)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Botile release metadata or package a tagged release."
    )
    parser.add_argument(
        "--tag",
        help="existing annotated tag to validate/package, e.g. v1.1.3",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="release output directory (default: dist)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate metadata only; no files are written",
    )
    args = parser.parse_args()

    metadata = read_metadata(PLUGIN)
    version = str(metadata["__version__"])

    if not args.check and not args.tag:
        fail("use --check, or pass --tag vMAJOR.MINOR.PATCH to package")

    if args.tag:
        if tag_version(args.tag) != version:
            fail(
                f"tag {args.tag} does not match __version__ {version} in "
                "Botile.plugin"
            )
        require_existing_tag(args.tag)

    if args.check:
        print(f"release metadata OK: id={metadata['__id__']} version={version}")
        return

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    package(version, output_dir)


if __name__ == "__main__":
    main()
