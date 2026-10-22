# Security policy / Политика безопасности

## English

### Reporting a vulnerability

Please report security issues **privately** through GitHub Security Advisories:

<https://github.com/iamvxrn/Botile/security/advisories/new>

Do not open a public issue with exploit details, a token, a phone number, a chat
ID, or another person's data. If GitHub private advisories are unavailable,
contact the maintainer through the private contact method on the
`@iamvxrn` GitHub profile before disclosing details publicly.

Include, when available:

- affected Botile version or commit;
- exteraless build, plugin SDK, Android version, and device;
- a minimal reproduction and the relevant `adb logcat` lines;
- impact/attack scenario and whether `hooks` is enabled;
- a suggested fix, if you have one.

### Scope

Relevant reports include:

- plugin code execution or permission-boundary issues;
- unsafe Java hook behavior, crashes, or unintended access to client data;
- release integrity problems, workflow injection, or tag/asset tampering;
- leaked credentials or personal data in the repository, logs, or releases.

Botile intentionally requests only the `hooks` permission. It does not request
network, file, message, or shell access. Host-side mocks and release checks are
not a substitute for Android testing.

### Supported versions

Security fixes are applied to the current `main` branch and the latest published
release. Older releases are handled on a best-effort basis; users should verify
the release checksum and upgrade when possible.

### Release integrity

Release assets are `Botile-<version>.plugin` and `SHA256SUMS`. The plugin asset
is a byte-for-byte copy of the tagged `Botile.plugin`; verify it before
installing:

```bash
sha256sum -c SHA256SUMS
```

The release workflow requires an existing `vMAJOR.MINOR.PATCH` tag, validates
the tag against `__version__`, and is the only workflow with `contents: write`.
Pull-request CI is read-only and does not receive repository secrets.

## Русский

### Сообщение об уязвимости

Сообщайте о проблемах безопасности **приватно** через GitHub Security
Advisories:

<https://github.com/iamvxrn/Botile/security/advisories/new>

Не открывайте публичный issue с деталями эксплуатации, токеном, телефоном,
chat ID или чужими данными. Если приватные advisories недоступны, свяжитесь с
maintainer через приватный способ связи в профиле `@iamvxrn` до публичного
раскрытия деталей.

По возможности укажите:

- затронутую версию или коммит Botile;
- сборку exteraless, SDK плагинов, версию Android и устройство;
- минимальное воспроизведение и соответствующий `adb logcat`;
- влияние/сценарий атаки и включён ли `hooks`;
- предложенное исправление, если оно есть.

### Область

К таким сообщениям относятся:

- выполнение кода плагина или проблемы границ разрешений;
- небезопасное поведение Java-хуков, падения или нежелательный доступ к данным
  клиента;
- проблемы целостности релизов, инъекции в workflow или подмена тегов/ассетов;
- утечки credentials или личных данных в репозитории, журналах или релизах.

Botile намеренно запрашивает только `hooks`; сеть, файлы, сообщения и shell не
запрашиваются. Host-side моки и release-проверки не заменяют тестирование на
Android.

### Поддерживаемые версии

Исправления безопасности применяются к текущей ветке `main` и последнему
опубликованному релизу. Более старые релизы поддерживаются по возможности;
пользователям следует проверять checksum релиза и обновляться.

### Целостность релизов

Ассеты релиза — `Botile-<version>.plugin` и `SHA256SUMS`. Плагин является
побайтовой копией `Botile.plugin` из тега; проверяйте его перед установкой:

```bash
sha256sum -c SHA256SUMS
```

Release workflow требует существующий тег `vMAJOR.MINOR.PATCH`, сверяет тег с
`__version__`, и только он имеет `contents: write`. CI для pull request
read-only и не получает секреты репозитория.
