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

Published tags and releases:

| Tag | Commit | Release |
|---|---|---|
| `v1.1.0` | `f2dfd528f10b4d66eea6d2e83f1c58117764e84d` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.0) |
| `v1.1.1` | `aaf46babf172e1147d07d3abbcfd0d837be9ada6` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.1) |
| `v1.1.3` | `62fbb689e94dd0ac7e2582f821c321aab6807204` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.3) |

There is no `1.1.2` commit, tag, or release. Do not create one retroactively.

For future releases, merge the version commit to `main` through a pull request
and wait for the required CI check. Then create and push an annotated
`vMAJOR.MINOR.PATCH` tag at that exact commit. The tag workflow validates the version, reruns checks,
packages the plugin and `SHA256SUMS`, and publishes the GitHub Release. It never
creates or moves tags. Historical releases `v1.1.0` and `v1.1.1` were backfilled
manually from the exact plugin bytes in their commits because those commits
predate the release workflow.

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

GitHub currently protects `main` by requiring a pull request and the
`Syntax and host-side checks` CI job, enforces linear history, blocks force
pushes/deletion, and protects `v*.*.*` tags from updates/deletion. Pull requests
require zero approvals because this repository currently has one maintainer.
GitHub Actions must be pinned to full commit SHAs. These are repository settings
in addition to the workflows and policy files in the repository.

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

Опубликованные теги и релизы:

| Тег | Коммит | Релиз |
|---|---|---|
| `v1.1.0` | `f2dfd528f10b4d66eea6d2e83f1c58117764e84d` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.0) |
| `v1.1.1` | `aaf46babf172e1147d07d3abbcfd0d837be9ada6` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.1) |
| `v1.1.3` | `62fbb689e94dd0ac7e2582f821c321aab6807204` | [GitHub Release](https://github.com/iamvxrn/Botile/releases/tag/v1.1.3) |

В репозитории нет коммита, тега или релиза `1.1.2`. Не создавайте их задним
числом.

Для будущих релизов смерджите коммит версии в `main` через pull request и
дождитесь обязательной проверки CI. Затем создайте и отправьте аннотированный
тег `vMAJOR.MINOR.PATCH` на этот коммит. Tag workflow проверит версию, повторно
запустит проверки, соберёт плагин и `SHA256SUMS`, затем опубликует GitHub
Release. Он не создаёт и не перемещает теги. Исторические релизы `v1.1.0` и
`v1.1.1` были вручную опубликованы из точных байтов плагина в их коммитах,
поскольку в тех коммитах ещё не было release workflow.

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

Сейчас GitHub защищает `main`: требуется pull request и проверка CI
`Syntax and host-side checks`, включена линейная история, запрещены force push
и удаление ветки; теги `v*.*.*` защищены от изменения и удаления. Для pull
request сейчас требуется ноль одобрений, так как у репозитория один мейнтейнер.
GitHub Actions должны быть привязаны к полным commit SHA. Это настройки GitHub
в дополнение к workflow и policy-файлам репозитория.

### Лицензия

В репозитории сейчас **нет LICENSE**. Не предполагайте право на
распространение и не добавляйте лицензию без решения владельца.
