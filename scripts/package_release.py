#!/usr/bin/env python3
"""Validate Botile metadata and build a distributable plugin asset."""

import argparse
import ast
import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "Botile.plugin"
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FIELDS = (
    "__id__",
    "__name__",
    "__version__",
    "__app_version__",
    "__sdk_version__",
    "__permissions__",
)


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(2)


def read_metadata():
    try:
        tree = ast.parse(PLUGIN.read_text(encoding="utf-8"), filename=str(PLUGIN))
    except (OSError, SyntaxError) as error:
        fail("cannot parse Botile.plugin: %s" % error)

    values = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in FIELDS:
            continue
        if target.id in values:
            fail("duplicate metadata: " + target.id)
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (TypeError, ValueError) as error:
            fail("metadata %s must be a literal: %s" % (target.id, error))

    missing = sorted(set(FIELDS) - values.keys())
    if missing:
        fail("missing metadata: " + ", ".join(missing))
    if values["__id__"] != "botile":
        fail("__id__ must be botile")
    if not isinstance(values["__version__"], str) or not VERSION_RE.fullmatch(
        values["__version__"]
    ):
        fail("__version__ must be strict MAJOR.MINOR.PATCH")
    for key in ("__app_version__", "__sdk_version__"):
        value = values[key]
        if not isinstance(value, str) or not value.strip():
            fail("%s must be a non-empty string" % key)
    permissions = values["__permissions__"]
    if not isinstance(permissions, (list, tuple)) or "hooks" not in permissions:
        fail("__permissions__ must declare hooks")
    return values


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path):
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def main():
    parser = argparse.ArgumentParser(description="Validate/package Botile.")
    parser.add_argument("--check", action="store_true", help="validate only")
    parser.add_argument("--tag", help="tag to validate, e.g. v1.2.0")
    parser.add_argument("--output-dir", default="dist", help="output directory")
    args = parser.parse_args()

    metadata = read_metadata()
    version = metadata["__version__"]
    if args.tag is not None:
        match = TAG_RE.fullmatch(args.tag)
        if match is None:
            fail("tag must be vMAJOR.MINOR.PATCH: %s" % args.tag)
        if ".".join(match.groups()) != version:
            fail("tag %s does not match plugin version %s" % (args.tag, version))
    if args.check:
        print("metadata OK: id=%s version=%s" % (metadata["__id__"], version))
        return

    output = Path(args.output_dir)
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)

    asset = output / ("Botile-%s.plugin" % version)
    shutil.copyfile(PLUGIN, asset)
    digest = sha256(asset)
    if digest != sha256(PLUGIN):
        fail("packaged asset does not match Botile.plugin")
    checksums = output / "SHA256SUMS"
    checksums.write_text(
        "%s  %s\n" % (digest, asset.name), encoding="ascii", newline="\n"
    )
    print("asset=%s" % display_path(asset))
    print("sha256=%s" % digest)
    print("checksums=%s" % display_path(checksums))


if __name__ == "__main__":
    main()
