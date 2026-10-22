# Botile

**Give bots a distinct avatar shape.**

Version **1.1.0**. Botile renders Telegram bot avatars as rounded squares while
leaving regular users, groups, channels, and custom images at the radius the
client chose.

## Update / install

1. Install `Botile.plugin` over the existing Botile installation. If your
   client keeps the old file, uninstall Botile first and install this file
   again.
2. On the install sheet, check **Java hooks (full control)**. Botile cannot
   modify Java views without the `hooks` permission. If you install without it,
   Botile logs a clear message and stays inactive.
3. Enable Botile.
4. Confirm the loaded file is actually 1.1.0. The plugin log should begin with:

   ```text
   Botile 1.1.0 starting (installed metadata version=1.1.0)
   ```

No root, LSPosed, APK modification, network access, or extra Python packages are
used. The only declared permission is `hooks`, implemented by exteraless's
in-process Aliuhook plugin runtime.

### Version range

The metadata minimum is set to the build actually inspected and verified at the
API level:

- `__app_version__ = ">=12.10.6"`
- `__sdk_version__ = ">=1.4.5.3"`

The same classes/methods/signatures were also inspected in the current source
(`13.0.2`, SDK `1.4.5.7`), so that range is source-compatible. An older
documentation baseline (`12.5.1` / SDK `1.4.4.3`) was **not** verified for this
plugin's exact hook and filter surface, so Botile does not claim it. This is a
metadata/range statement, not proof that either build renders correctly on a
phone.

## What changed from 1.0

v1 was not device-verified. It installed but produced no visible change, and on
a successful load it logged only the load-time line `Botile active` — no
invocation, entity, or radius evidence.

I inspected the actual exteraless APK found on this machine:

- APK: `exteraless-v12.10.6-00c14f4(1261).apk`
- package: `com.exteraless.app`
- app version: `12.10.6-00c14f4`
- plugin SDK version: `1.4.5.3`
- Python: `3.11`

The APK contains the exact target v1 used:

- `org.telegram.ui.Cells.DialogCell.update(int, boolean)` — `(I Z)Z`
- `DialogCell.avatarImage: ImageReceiver` (public)
- `DialogCell.user: TLRPC.User` (private)
- `DialogCell.customDialog` (private)
- `org.telegram.messenger.ImageReceiver.setRoundRadius(int)` — `(I)V`
- `ImageReceiver.setRoundRadius(int[])` — `([I)V`
- `ImageReceiver.setAvatarCornersApplied(boolean)` — `(Z)V`
- `org.telegram.tgnet.TLRPC$User.bot` (public boolean)

So the v1 failure was **not** an invented class, method, field, or version
rejection. It was a silent runtime failure. The remaining candidates all looked
identical from the outside:

1. the `hooks` permission was not granted / the plugin was not trusted;
2. native hook initialization was disabled or broken;
3. the hook was registered but never invoked;
4. v1's private-field reflection returned `None`;
5. the radius was applied but overwritten later.

v1 logged only load-time text. It did not log whether the hook was invoked,
which entity it saw, or whether the radius override stuck, so in practice the
failure was silent. This version removes v1's private-field dependency entirely
and logs hook registration, first invocation, bot detection, radius overrides,
read-back radius, custom-image clearing, and failures. **A device log is still
required before calling the visual problem fixed.**

## Coverage matrix

| UI surface | Implementation | Status |
|---|---|---|
| Main dialog list | `ImageReceiver.setForUserOrChat` + `setRoundRadius`; `DialogCell.update` fallback | Implemented; static/mock tested; device pending |
| Dialog search results using `DialogCell` | Same central hooks + `DialogCell` fallback | Implemented; static/mock tested; device pending |
| Search results using `ProfileSearchCell` | Direct `ImageReceiver.setImage(..., parentObject=user/chat, ...)` with parent-class allowlist | Implemented; static/mock tested; device pending |
| Sender avatars in private/group messages (`ChatMessageCell`) | Central bind + radius hooks | Implemented; static/mock tested; device pending |
| Group member lists and share sheets (`UserCell`, `ShareDialogCell`, `HintDialogCell`) | Central bind + radius hooks | Implemented; static/mock tested; device pending |
| Chat header avatar (`ChatAvatarContainer`) | Central bind + radius hooks | Implemented; static/mock tested; device pending |
| Bot profile, normal photo (`ProfileActivity$AvatarImageView`) | Direct `setImage` parent allowlist + radius hook | Implemented; static/mock tested; device pending |
| Bot profile, normal photo (`ProfileActivity2$AvatarImage`) | Direct `setImage` parent allowlist + radius hook | Implemented; static/mock tested; device pending |
| Reply previews / forwarded mini avatars (`AvatarSpan`) | Central `setForUserOrChat` + radius hooks | Implemented; static/mock tested; device pending |
| Other widgets using `ImageReceiver.setForUserOrChat` | Central hooks | Implemented; static/mock tested; device pending |
| Bot profile vector/video avatar set only through `setImageBitmap` | No TLRPC entity is available at that call site | **Not covered reliably**; documented limitation |
| Full-screen photo viewer | Intentionally excluded (a photo is not an avatar) | Not covered by design |
| Notifications and non-UI rendering | No `ImageReceiver` avatar path | Not covered |

## How it works

### 1. Bind hook

```text
ImageReceiver.setForUserOrChat(TLObject, Drawable, Object, boolean, int, boolean)
```

The after-hook reads the actual `TLRPC.User`/`TLRPC.Chat` argument. If it is a
user with `bot == true`, the receiver is marked in its public `mark` field and
the **full four-corner radius** (including `0,0,0,0` and asymmetric values) is
stored in a `java.util.WeakHashMap`. The pre-existing `mark` object is saved
first; it is restored only if the receiver still carries Botile's marker.
Weak keys mean Botile does not keep dialog cells or image receivers alive.

### 2. Radius hook

```text
ImageReceiver.setRoundRadius(int[])
```

A Java-side filter runs Python only when the receiver carries Botile's marker.
The hook:

- copies the app's requested four-corner radius as the restore baseline;
- forces all four corners to Botile's radius;
- lets the original method execute;
- after the call, reads the receiver's radius back and logs whether the
  override actually stuck.

Restoration passes the saved `int[4]` back to `setRoundRadius(int[])`, so
zero and asymmetric corners are not flattened. Marker restoration is guarded:
a mark set by someone else after Botile is left untouched.

This is what makes Botile survive callers that set the radius *after*
`setForUserOrChat` (the original `DialogCell.update` does exactly that).

The maximum radius is 11 dp, matching the dialog-list requirement. It is scaled
down for very small avatars so an 18 dp forwarded/reply mini avatar does not
turn into a circle:

```text
radius_px = round(avatar_width_px * 0.22), capped at 11 dp
```

### 3. Custom images

`ImageReceiver.setImage(...)` and `setImageBitmap(...)` are filtered by the
same marker. When a non-entity/custom image replaces a bot avatar, Botile
restores the stored baseline radius and clears the marker. Calls made inside
`setForUserOrChat` are skipped with a thread-local depth flag, because the
after-bind hook handles them.

### 4. Direct-image avatars

Profile headers and `ProfileSearchCell` do not use `setForUserOrChat`; they call
`ImageReceiver.setImage(..., parentObject=user/chat, ...)`. Botile has a
Java-side filter for `TLRPC.User`/`TLRPC.Chat` at argument 9, then checks the
receiver's parent class against:

```text
org.telegram.ui.ProfileActivity$AvatarImageView   (including $1 anonymous subclass)
org.telegram.ui.ProfileActivity2$AvatarImage
org.telegram.ui.Cells.ProfileSearchCell
```

Only those known avatar containers (and subclasses with a `$...` suffix) are
modified. Unknown bot-parent containers are logged once with their class name
instead of silently shaping arbitrary images.

### 5. Dialog fallback

`DialogCell.update(int, boolean)` is still hooked after the original. It only
re-applies the radius when the cell's `avatarImage` carries Botile's marker.
This is a small fallback for the main dialog list; it no longer depends on
private `DialogCell` fields.

### Recycling, accounts, unloading

- `DialogCell` and message-cell rebinding always call `setForUserOrChat` again,
  which updates the mark/baseline for the new entity.
- A bot → regular user/group/channel transition restores the stored radius.
- A regular user → bot transition marks and applies the bot radius.
- Bot detection uses the entity attached to the receiver, not the selected
  account.
- On unload, all hooks are removed and every tracked receiver is restored to
  its baseline radius on the UI thread.

## Diagnostics and device validation

Botile's logger writes through `self.log` into the exteraless plugin log
(`PluginLog` / `FileLog`, prefixed `[plugin:botile]`).

### Collect logs

```bash
adb logcat -c
# open the main chat list, scroll through bots/users/groups/channels,
# open a bot chat and a bot profile
adb logcat -d -v time | grep -i "botile"
```

Also check the in-app plugin log: **Settings → Plugins → Botile → log**.

### Expected successful sequence

```text
Botile 1.1.0 starting (installed metadata version=1.1.0)
diag hooks permission=True
diag sdk=1.4.5.3
hook bind: installed ImageReceiver.setForUserOrChat
hook radius: installed ImageReceiver.setRoundRadius(int[])
hook image: installed ImageReceiver.setImage core
hook bitmap: installed ... setImageBitmap overload(s)
hook dialog: installed DialogCell.update fallback
Botile hooks: bind=OK radius=OK image=OK dialog=OK
diag first bind: entity=org.telegram.tgnet.TLRPC$TL_user id=... bot=true parent=...
diag first bot detected: id=... parent=...
diag radius verified in receiver ...
diag first radius override: requested=... parent=... -> ...px
```

Then scrolling should produce periodic summaries such as:

```text
diag periodic: binds=500 bots=... nonbots=... overrides=... verified=... clears=...
```

### Failure decision tree

| Log evidence | Meaning / next step |
|---|---|
| No `Botile 1.1.0 starting` line | Plugin is not loaded/enabled, or the installed file is still 1.0. Reinstall and check **Plugins → Botile**. |
| `diag hooks permission=False` | Grant the **hooks** permission, then disable/re-enable Botile. |
| `diag native_hooks ready=False broken=True` | Exteraless disabled native hooks after a crash. Restart/reinstall the client and clear the plugin engine's native-hook failure state; without Aliuhook Botile cannot work. |
| `hook bind: FAILED ...` | The inclusive hook runtime rejected/reflection-failed the method. The log includes the exact method and exception. |
| `binds=0` after scrolling and opening chats | The bind hook is installed but not invoked. Include the full log and the exact exteraless build in a report. |
| `binds>0`, `bots=0` | The bind hook runs but the entity is not seen as a bot. Include the first-bind entity class/id log. |
| `bots>0`, `overrides=0` | The radius filter never matched or the radius hook did not run. Check for `HookFilter` errors and the hook registration lines. |
| `diag radius override did not stick` | The Java method ran but the receiver's radius read back differently. This points to a later overwrite or a build difference. |
| `diag direct avatar parent not covered: ...` | A direct-image avatar surface is not in the allowlist. Send the logged class name; it can be added as a targeted hook. |
| `overrides>0`, `verified>0`, but no visual change | The receiver value is correct but the drawable/clip path is not honoring it on that surface. This must be checked with a device screenshot and the relevant parent class. |

**No Android runtime log exists for this implementation yet.** Static analysis
and mocks cannot prove pixels on screen. Do not mark Botile visually fixed until
the log shows `binds>0`, `bots>0`, `overrides>0`, `verified>0` and a device
screenshot shows rounded-square bot avatars with circular regular users.

## Verification performed

### Actually performed here

- Python syntax compile — passed (`python3` 3.14 host; source uses syntax
  compatible with the app's Python 3.11).
- Metadata parsed with exteraless's actual AST parser:
  `id=botile`, `name=Botile`, `description=Give bots a distinct avatar shape.`,
  `version=1.1.0`, `permissions=["hooks"]`, no requirements.
- Actual exteraless capability scan: only `hooks`, no network/files/message
  permission markers.
- Mock behavioral harness passed, including
  `python3 tests/test_state_preservation.py`:
  - bot bind marks receiver and applies the 11 dp maximum;
  - dialog's later `setRoundRadius` is overridden and read back;
  - regular-user recycle restores the baseline and clears the mark;
  - group/channel recycle restores the baseline;
  - bot → user → bot recycling;
  - a `0,0,0,0` baseline is restored exactly on bot → non-bot and on unload;
  - asymmetric `[10,20,30,40]` baselines are preserved through bot → non-bot,
    the radius hook, and unload;
  - a pre-existing `mark` is saved and restored;
  - a later external mark is left untouched during clear/unload;
  - direct profile/search parent paths apply and restore;
  - unknown direct parent is refused and logged;
  - custom `setImage` and `setImageBitmap` clear bot styling;
  - `DialogCell` fallback only touches marked receivers;
  - unload unhooks and restores baselines;
  - denied hooks, missing `ImageReceiver`, and failed bind registration fail
    gracefully and log the reason;
  - a small avatar receives a proportionally smaller radius.

### Statically verified against source/APK

- Installed APK `12.10.6-00c14f4(1261)`: SDK `1.4.5.3`; target methods, fields,
  `setForUserOrChat` overloads, core `setImage` signature, and
  `setRoundRadius(int[])` all exist.
- GitHub source at `00c14f4` confirms `DialogCell.update` calls
  `setAvatarCornersApplied(true)` followed by `setRoundRadius(...)`, and the
  avatar is set through `setForUserOrChat` or direct `setImage` with the entity
  as `parentObject`.
- `ProfileActivity$AvatarImageView`, `ProfileActivity2$AvatarImage`,
  `ProfileSearchCell`, and `AvatarSpan` paths were checked for their parent
  view/entity arguments.
- Plugin lifecycle, permission key, `HookFilter` condition/or support, and
  `.plugin` installation format were checked against the exteraless source.

### Requires a real Android device

Everything visual remains device-pending:

- avatar rendering and actual corner shape;
- scrolling/recycling smoothness;
- account switching;
- enable/disable restoration of visible cells;
- profile/header/forward surfaces;
- native Aliuhook initialization.

## Known limitations

- Bot profile **vector/video** avatars set through a direct
  `setImageBitmap(...)` call have no TLRPC entity at that call site. Normal
  profile photos are covered; the vector path is not guaranteed.
- Full-screen photo viewers and notifications are intentionally not avatar
  targets.
- Enabling Botile on an already-rendered screen does not force a global list
  reload. Cells update on their next bind/update. This avoids extra permissions
  and UI churn; the next normal scroll/bind applies the style.
- For non-bots, Botile preserves the client's current avatar-corner setting.
  If that setting already rounds everyone, Botile does not override it.
- The radius is capped at 11 dp and scaled down for tiny avatars; profile
  avatars therefore get an 11 dp maximum rather than a large proportional
  radius.
- The plugin still requires the `hooks` permission and trusted level. It cannot
  work in isolated/gated mode.
- Future client changes are reported by the diagnostic logs rather than
  silently producing no effect.

## Source references

Verified against:

- installed APK `exteraless-v12.10.6-00c14f4(1261).apk`
  (`com.exteraless.app`, SDK `1.4.5.3`, Python 3.11);
- GitHub `exteraless/exteraless` commit
  [`00c14f4`](https://github.com/exteraless/exteraless/commit/00c14f4)
  (matching the APK version string);
- current main commit `8b7ec40` where relevant.

Key files/classes:

| File | What was verified |
|---|---|
| `TMessagesProj/src/main/java/org/telegram/messenger/ImageReceiver.java` | `setForUserOrChat(...)`, core 11-arg `setImage(...)`, `setRoundRadius(int[])`, `getRoundRadius()`, `setAvatarCornersApplied()`, `setMark/getMark` |
| `TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java` | `avatarImage`, `update(int, boolean)`, radius application via `setRoundRadius` |
| `TMessagesProj/src/main/java/org/telegram/tgnet/TLRPC.java` | `TLRPC.User.bot` |
| `TMessagesProj/src/main/java/org/telegram/ui/Cells/ProfileSearchCell.java` | direct `setImage(..., parentObject=user/chat, ...)` and avatar radius |
| `TMessagesProj/src/main/java/org/telegram/ui/ProfileActivity.java` | `ProfileActivity$AvatarImageView` direct avatar path |
| `TMessagesProj/src/main/java/org/telegram/ui/ProfileActivity2.java` | `ProfileActivity2$AvatarImage` direct avatar path |
| `TMessagesProj/src/main/java/org/telegram/ui/AvatarSpan.java` | forwarded/reply mini avatars use `setForUserOrChat` |
| `TMessagesProj/src/main/java/app/exteraless/plugins/xposed/HookFilter.java` | Java-side `condition`, `or`, `argument_is_instance_of` filters |
| `TMessagesProj/src/main/java/app/exteraless/plugins/PluginPermissions.java` | `hooks` permission |
| `TMessagesProj/src/main/python/base_plugin.py` | `MethodHook`, `HookFilter`, `hook_method`, lifecycle |
| `TMessagesProj/src/main/python/hook_utils.py` | `find_class`; v1's private-field helper is no longer used |

## Files

- `Botile.plugin` — installable plugin (Python source with metadata), version
  1.1.0.
- `README.md` — this English document.
- `README.ru.md` — Russian documentation.
- `VALIDATION.md` — bilingual English/Russian phone validation protocol.
- `tests/test_state_preservation.py` — host-side radius/mark state mocks
  (zero and asymmetric corners, bot→non-bot, unload, marker preservation).
