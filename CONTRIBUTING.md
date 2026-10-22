# Contributing / Участие в разработке

## English

### Scope

Botile is a small exteraless Python plugin. Keep changes focused on the bot
avatar shape/outline, compatibility, documentation, tests, or release
engineering. Runtime changes and release-engineering changes should be separate
pull requests.

Do not add a license, change the plugin version, create a tag, or publish a
release unless the repository owner explicitly asks for it.

### Checks

Use Python 3.11 and only the standard library:

```bash
python3 scripts/package_release.py --check
python3 tests/test_state_preservation.py
python3 - <<'PY'
import py_compile
py_compile.compile("Botile.plugin", cfile="/tmp/Botile.plugin.pyc", doraise=True)
print("plugin syntax OK")
PY
```

CI runs the same checks on pull requests to `main`, pushes to `main`, and manual
dispatches. Host-side mocks do not prove Android rendering; runtime changes need
a device log and screenshots as described in `VALIDATION.md`.

### Pull requests

- Target `main`; use a short branch and a reviewable diff.
- Keep English and Russian documentation consistent.
- Update `VALIDATION.md` when the phone-test protocol changes.
- Never include tokens, phone numbers, chat IDs, or other personal data in logs
  or screenshots.
- Do not commit `dist/`, `__pycache__/`, virtual environments, or local build
  output.
- Add tests for state-machine or parser changes; do not weaken existing tests to
  make a change pass.

### Release procedure

`Botile.plugin`'s `__version__` is the version source of truth. Release tags use
strict `vMAJOR.MINOR.PATCH` and **must already exist** before the release
workflow runs. The workflow has `contents: write` permission only for publishing
the release, validates the tag against `__version__`, and uses
`gh release create --verify-tag`; it never creates or moves a tag.

Historical tag plan:

| Tag | Commit | Notes |
|---|---|---|
| `v1.1.0` | `f2dfd528f10b4d66eea6d2e83f1c58117764e84d` | Initial 1.1.0 source commit |
| `v1.1.1` | `aaf46babf172e1147d07d3abbcfd0d837be9ada6` | 1.1.1 source commit |
| `v1.1.3` | commit created from the current pending working tree | Pending; do not tag before it is committed |

There is **no 1.1.2 commit** in this repository. Do not create a `v1.1.2` tag or
release.

Release steps, after review and approval:

1. Merge the approved commit to `main` and wait for CI to pass.
2. From a clean checkout of that exact commit, verify
   `git status --short` is empty and `python3 scripts/package_release.py --check`
   passes.
3. Create the tag manually, for example:
   `git tag -a v1.1.3 <commit> -m "Botile 1.1.3"`.
4. Review the tag, then push only that tag:
   `git push origin v1.1.3`.
5. The tag-triggered `Release` workflow re-runs the CI checks, verifies strict
   tag/version equality and the tag-to-HEAD relationship, packages
   `Botile-<version>.plugin` plus `SHA256SUMS`, and publishes generated notes.
6. Backfill historical releases in chronological order (`v1.1.0`, then
   `v1.1.1`, then the next release) so GitHub's "Latest" release is not an old
   backfilled release. Verify the "Latest" label afterward.

The release workflow refuses to run the package step on a dirty worktree. Do not
add automation that creates tags from a version bump, a pull request, or an
arbitrary commit.

#### Historical backfill

The release workflow is introduced in the 1.1.3 commit, so the `v1.1.0` and
`v1.1.1` tags predate the workflow file. After reviewing those tags, create
their two releases manually with the exact bytes from the tags; do not invent a
1.1.2 release:

```bash
test "$(git rev-parse v1.1.0^{commit})" = "f2dfd528f10b4d66eea6d2e83f1c58117764e84d"
tmp="$(mktemp -d)"
git archive f2dfd52 Botile.plugin | tar -x -C "$tmp"
cp "$tmp/Botile.plugin" "$tmp/Botile-1.1.0.plugin"
(cd "$tmp" && sha256sum Botile-1.1.0.plugin > SHA256SUMS)
gh release create v1.1.0 \
  --verify-tag \
  --latest=false \
  --title "Botile 1.1.0" \
  --generate-notes \
  "$tmp/Botile-1.1.0.plugin" "$tmp/SHA256SUMS"
```

Repeat for `v1.1.1` and `aaf46ba` using the same pattern. Run the historical
releases in chronological order before the next release, and check GitHub's
"Latest" label afterward.

### Local packaging

From a clean checkout of an existing tag:

```bash
python3 scripts/package_release.py --tag v1.1.3 --output-dir dist
(cd dist && sha256sum -c SHA256SUMS)
```

Output is intentionally ignored by Git:

```text
dist/Botile-1.1.3.plugin
dist/SHA256SUMS
```

`Botile-1.1.3.plugin` is a byte-for-byte copy of `Botile.plugin`. The script
does not create tags or releases.

### Repository settings

The owner should enable branch protection for `main` with the CI job as a
required check, protect `v*` tags, and require review before publishing a
release. These are GitHub settings, not repository files.

### License

This repository currently has **no LICENSE file**. Do not assume permission to
redistribute or add a license without the owner's decision.

## Русский

### Область изменений

Botile — небольшой Python-плагин для exteraless. Держите изменения в рамках
формы/обводки bot-аватаров, совместимости, документации, тестов или release
engineering. Изменения runtime и release engineering лучше делать отдельными
pull request.

Не добавляйте лицензию, не меняйте версию плагина, не создавайте тег и не
публикуйте релиз без явного указания владельца репозитория.

### Проверки

Python 3.11, только стандартная библиотека:

```bash
python3 scripts/package_release.py --check
python3 tests/test_state_preservation.py
python3 - <<'PY'
import py_compile
py_compile.compile("Botile.plugin", cfile="/tmp/Botile.plugin.pyc", doraise=True)
print("plugin syntax OK")
PY
```

CI запускает те же проверки для pull request в `main`, push в `main` и ручного
запуска. Host-side моки не доказывают отрисовку Android; для runtime-изменений
нужны журнал с устройства и скриншоты по `VALIDATION.md`.

### Pull requests

- Целевая ветка — `main`; короткая ветка и reviewable diff.
- Английская и русская документация должны совпадать по смыслу.
- При изменении протокола проверки обновляйте `VALIDATION.md`.
- Не добавляйте токены, телефоны, chat ID и другие личные данные в журналы и
  скриншоты.
- Не коммитьте `dist/`, `__pycache__/`, virtualenv и локальные артефакты.
- Для изменений state machine или парсера добавляйте тесты; не ослабляйте
  существующие тесты ради прохождения проверки.

### Процесс релиза

Источник версии — `__version__` в `Botile.plugin`. Теги релизов — строго
`vMAJOR.MINOR.PATCH`; тег **должен уже существовать** до запуска release
workflow. Workflow получает `contents: write` только для публикации, проверяет
тег против `__version__` и вызывает `gh release create --verify-tag`; он никогда
не создаёт и не перемещает теги.

План исторических тегов:

| Тег | Коммит | Примечание |
|---|---|---|
| `v1.1.0` | `f2dfd528f10b4d66eea6d2e83f1c58117764e84d` | Исходный коммит 1.1.0 |
| `v1.1.1` | `aaf46babf172e1147d07d3abbcfd0d837be9ada6` | Исходный коммит 1.1.1 |
| `v1.1.3` | коммит из текущего рабочего дерева | Ожидает коммита; не тегировать заранее |

В репозитории **нет коммита 1.1.2**. Не создавайте тег или релиз `v1.1.2`.

Порядок после review и одобрения:

1. Смержить одобренный коммит в `main` и дождаться зелёного CI.
2. В чистом checkout этого коммита проверить, что `git status --short` пуст, а
   `python3 scripts/package_release.py --check` проходит.
3. Создать тег вручную, например:
   `git tag -a v1.1.3 <commit> -m "Botile 1.1.3"`.
4. Проверить тег и отправить только его:
   `git push origin v1.1.3`.
5. Workflow `Release` заново запустит проверки CI, сверит строгую версию тега,
   версию в плагине и коммит, соберёт `Botile-<version>.plugin` и
   `SHA256SUMS`, затем опубликует release со сгенерированными notes.
6. Исторические релизы создавать по порядку (`v1.1.0`, затем `v1.1.1`, затем
   следующий), чтобы GitHub не сделал старый backfilled-релиз «Latest».
   Проверьте метку «Latest» после этого.

Release workflow откажется пакетировать грязное рабочее дерево. Не добавляйте
автоматизацию, которая создаёт теги из bump версии, pull request или случайного
коммита.

#### Исторические релизы

Release workflow появляется в коммите 1.1.3, поэтому теги `v1.1.0` и `v1.1.1`
старше самого workflow. После review этих тегов создайте два релиза вручную из
точных байтов тега; не придумывайте релиз 1.1.2:

```bash
test "$(git rev-parse v1.1.0^{commit})" = "f2dfd528f10b4d66eea6d2e83f1c58117764e84d"
tmp="$(mktemp -d)"
git archive f2dfd52 Botile.plugin | tar -x -C "$tmp"
cp "$tmp/Botile.plugin" "$tmp/Botile-1.1.0.plugin"
(cd "$tmp" && sha256sum Botile-1.1.0.plugin > SHA256SUMS)
gh release create v1.1.0 \
  --verify-tag \
  --latest=false \
  --title "Botile 1.1.0" \
  --generate-notes \
  "$tmp/Botile-1.1.0.plugin" "$tmp/SHA256SUMS"
```

Повторите для `v1.1.1` и `aaf46ba` по той же схеме. Создавайте исторические
релизы по порядку до следующего релиза и проверьте метку GitHub «Latest» после
этого.

### Локальная сборка

Из чистого checkout существующего тега:

```bash
python3 scripts/package_release.py --tag v1.1.3 --output-dir dist
(cd dist && sha256sum -c SHA256SUMS)
```

Результат намеренно игнорируется Git:

```text
dist/Botile-1.1.3.plugin
dist/SHA256SUMS
```

`Botile-1.1.3.plugin` — побайтовая копия `Botile.plugin`. Скрипт не создаёт ни
теги, ни релизы.

### Настройки репозитория

Владельцу следует включить защиту `main` с обязательной проверкой CI, защиту
тегов `v*` и требование review перед публикацией релиза. Это настройки GitHub,
а не файлы репозитория.

### Лицензия

В репозитории сейчас **нет LICENSE**. Не предполагайте право на
распространение и не добавляйте лицензию без решения владельца.
