# Changelog / История изменений

Notable changes to Botile. Source commits and releases are recorded separately;
a commit existing on `main` does not by itself mean that a GitHub Release was
published.

---

## 1.1.3 — released 2026-10-22 / опубликовано 2026-10-22

**English**

- Normalizes the Chaquopy class proxy to `java.lang.Class` before reflective
  method lookup, then selects the exact hook and `DialogCell` overloads.
- Adds an optional thin avatar outline for marked bot receivers. It is drawn
  after `ImageReceiver.draw(...)`, follows the active corner radius, uses the
  adaptive theme color, and leaves non-bot avatars untouched.
- Updates the English/Russian documentation, validation protocol, and host-side
  mocks.
- Adds read-only CI, a tag-triggered validated release workflow, a stdlib
  packaging/checksum script, repository templates, Dependabot for Actions, and
  release badges. These repository changes do not alter plugin runtime behavior.
- Status: published as [GitHub Release v1.1.3](https://github.com/iamvxrn/Botile/releases/tag/v1.1.3); the tag points to commit
  `62fbb689e94dd0ac7e2582f821c321aab6807204`.

**Русский**

- Прокси класса Chaquopy нормализуется в `java.lang.Class` перед reflection,
  после чего выбираются точные перегрузки хуков и `DialogCell`.
- Добавлена необязательная тонкая обводка помеченных bot-получателей. Она
  рисуется после `ImageReceiver.draw(...)`, повторяет текущий радиус, использует
  адаптивный цвет темы и не затрагивает не-ботов.
- Обновлены английская/русская документация, протокол проверки и host-side
  mock-тесты.
- Добавлены read-only CI, release workflow с проверкой тега, stdlib-скрипт
  сборки/checksum, шаблоны репозитория, Dependabot для Actions и release-бейджи.
  Эти изменения репозитория не меняют runtime-поведение плагина.
- Статус: опубликовано как [GitHub Release v1.1.3](https://github.com/iamvxrn/Botile/releases/tag/v1.1.3); тег указывает на коммит
  `62fbb689e94dd0ac7e2582f821c321aab6807204`.

---

## 1.1.1 — source commit `aaf46ba` / исходный коммит

**English**

- Replaced the singular `getDeclaredMethod()` lookup with
  `getDeclaredMethods()` and added tests for exact overload selection.
- Known issue: the lookup still ran on an unnormalized class proxy; version
  1.1.3 normalizes the proxy before reflection.
- Plugin metadata version: `1.1.1`.
- Published as [GitHub Release v1.1.1](https://github.com/iamvxrn/Botile/releases/tag/v1.1.1); the tag points to
  the commit above.

**Русский**

- Единичный вызов `getDeclaredMethod()` заменён на `getDeclaredMethods()`;
  добавлены тесты выбора точной перегрузки.
- Известная проблема: поиск всё ещё выполнялся на ненормализованном прокси
  класса; в версии 1.1.3 прокси нормализуется перед reflection.
- Версия в метаданных плагина: `1.1.1`.
- Опубликовано как [GitHub Release v1.1.1](https://github.com/iamvxrn/Botile/releases/tag/v1.1.1); тег
  указывает на коммит выше.

Commit: [`aaf46babf172e1147d07d3abbcfd0d837be9ada6`](https://github.com/iamvxrn/Botile/commit/aaf46babf172e1147d07d3abbcfd0d837be9ada6)

---

## 1.1.0 — source commit `f2dfd52` / исходный коммит

**English**

- Initial Botile plugin with centralized `ImageReceiver.setForUserOrChat`
  tracking, exclusive `setRoundRadius` handling, direct-avatar allowlisting,
  and a `DialogCell.update` fallback.
- Added English/Russian README files, the bilingual phone validation protocol,
  and the first host-side state-preservation tests.
- Plugin metadata version: `1.1.0`.
- Published as [GitHub Release v1.1.0](https://github.com/iamvxrn/Botile/releases/tag/v1.1.0); the tag points to
  the commit above.

**Русский**

- Первый плагин Botile: централизованное отслеживание
  `ImageReceiver.setForUserOrChat`, монопольная обработка `setRoundRadius`,
  allowlist прямых аватаров и fallback через `DialogCell.update`.
- Добавлены README на английском/русском, двуязычный протокол проверки на
  телефоне и первые host-side тесты сохранения состояния.
- Версия в метаданных плагина: `1.1.0`.
- Опубликовано как [GitHub Release v1.1.0](https://github.com/iamvxrn/Botile/releases/tag/v1.1.0); тег
  указывает на коммит выше.

Commit: [`f2dfd528f10b4d66eea6d2e83f1c58117764e84d`](https://github.com/iamvxrn/Botile/commit/f2dfd528f10b4d66eea6d2e83f1c58117764e84d)
