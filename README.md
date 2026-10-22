# Botile

[Русская версия](README.ru.md)

Botile renders Telegram bot avatars as rounded squares with a thin
theme-adaptive outline. Regular users, groups, channels, and custom images keep
the radius chosen by the client.

Current version: **1.1.3**.

## Install

1. Install `Botile-<version>.plugin` from a release, or `Botile.plugin` from a
   checkout. The release asset is a byte-for-byte copy of `Botile.plugin`; verify
   it against `SHA256SUMS` when one is provided.
2. Select **Java hooks (full control)** on the install sheet and keep Botile at
   **Trusted**. Without the `hooks` permission the plugin stays inactive.
3. Enable Botile and confirm the log starts with
   `Botile 1.1.3 starting`.
4. If an old Botile file remains installed, uninstall it and install the new
   file again.

No root, LSPosed, APK modification, network access, or extra Python packages are
needed. The only declared permission is `hooks`.

## Compatibility

- exteraless `>= 12.10.6`
- plugin SDK `>= 1.4.5.3`

The target methods and signatures were checked against exteraless
`12.10.6-00c14f4` (SDK `1.4.5.3`). The same hook surface was also checked in
the current source (`13.0.2`, SDK `1.4.5.7`), so the declared range is
source-compatible. This is not a claim that every UI surface has been verified
on every build.

## What it does

- Bot detection comes from the `TLRPC.User`/`TLRPC.Chat` entity passed to
  `ImageReceiver.setForUserOrChat(...)`.
- Marked bot receivers are forced to the Botile radius through
  `ImageReceiver.setRoundRadius(int[])`. The original four-corner radius,
  including zero and asymmetric values, is saved and restored.
- Profile headers and search results that pass the entity through
  `ImageReceiver.setImage(..., parentObject=...)` are supported through a
  narrow parent allowlist.
- `setImageBitmap(...)` and custom `setImage(...)` calls clear bot state.
- A thin outline is added after `ImageReceiver.draw(Canvas,
  BackgroundThreadDrawHolder)`: 1 dp inside the image bounds, following the
  current corner radius, using `Theme.key_windowBackgroundWhiteBlackText` at 45%
  alpha. Non-bots are filtered out before the Python callback.
- All hooks are removed and tracked radii/marks are restored on unload.

The outer avatar shape is always left to the client for non-bots. Botile does
not replace the image, view, drawable, or renderer.

## Limitations

- Bot profile vector/video avatars set only through `setImageBitmap(...)` have
  no entity at that call site and may not be covered.
- Full-screen photos and notifications are not avatar targets.
- Background-thread draws with a non-null holder are skipped by the outline.
- The outline uses the global theme color, not a per-chat `ResourcesProvider`.
- Enabling Botile does not force a global list reload; cells update on their next
  bind or update.
- Host-side mocks do not prove Android rendering. Device testing is still
  required after runtime changes.

## Development

Python 3.11 and the standard library are sufficient:

```bash
python3 -m py_compile Botile.plugin
python3 scripts/package_release.py --check
python3 tests/test_state_preservation.py
python3 scripts/package_release.py --output-dir dist
(cd dist && sha256sum -c SHA256SUMS)
```

The package output is:

```text
dist/Botile-1.1.3.plugin
dist/SHA256SUMS
```

The plugin metadata is the version source of truth. Releases are tag-triggered:
an existing `vMAJOR.MINOR.PATCH` tag runs syntax, metadata, and mock checks,
verifies the tag against `__version__`, packages and checksums the plugin, then
publishes `Botile-<version>.plugin` and `SHA256SUMS` with generated notes. The
workflow never creates or moves tags. There is currently no LICENSE file; do
not redistribute or add a license without the owner's decision.

## Phone check

After installing on exteraless:

1. Open the main chat list with a bot, user, group, and channel.
2. Check that the bot is a rounded square with a thin outline; users, groups,
   and channels keep their shape and have no Botile outline.
3. Repeat in light and dark themes, a bot chat, a bot profile, and a forwarded
   or reply preview. Scroll to force cell recycling.
4. Collect `adb logcat` and screenshots. Useful lines include
   `diag hooks permission=True`, `hook bind: installed`,
   `hook border: installed draw outline`, and `diag first bind: ... bot=True`.

Report bugs with the Botile version, exteraless build/SDK, device/Android
version, relevant log lines, and screenshots. Report security issues privately
through GitHub Security Advisories rather than a public issue.
