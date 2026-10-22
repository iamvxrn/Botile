# Botile phone validation / Проверка Botile на телефоне

This protocol is for an exteraless build on a real Android device. It does not
claim that Botile already works visually. Record the build, logs, and
screenshots; do not mark a step passed from logs alone.

Этот протокол предназначен для сборки exteraless на реальном Android-устройстве.
Он не утверждает, что Botile уже визуально работает. Записывайте сборку,
журналы и скриншоты; не отмечайте шаг пройденным только по журналу.

## Prerequisites / Предварительные условия

- exteraless `>= 12.10.6` with plugin SDK `>= 1.4.5.3` (Botile metadata minimum).
- Botile `1.1.0` installed and enabled.
- The **hooks** permission granted and trust level **Trusted**. Without it the
  log contains `diag hooks permission=False`.
- ADB access from the computer: `adb devices` lists the phone.
- The phone is connected to the same Telegram account used for testing.

- exteraless `>= 12.10.6` с SDK плагинов `>= 1.4.5.3` (минимум в метаданных
  Botile).
- Botile `1.1.0` установлен и включён.
- Разрешение **hooks** выдано, уровень доверия **Trusted**. Без этого в журнале
  будет `diag hooks permission=False`.
- ADB с компьютера: `adb devices` показывает телефон.
- Телефон подключён к тестовому аккаунту Telegram.

## Start a session / Начало сессии

```bash
adb logcat -c
# open exteraless, the main chat list, then the cases below
# откройте exteraless, основной список чатов, затем кейсы ниже
adb logcat -d -v time | grep -i "botile" > botile-log.txt
```

Also save screenshots for each visual case. Include the exteraless version from
**Settings → About** and the Botile version from **Settings → Plugins → Botile**.

Также сохраните скриншоты для каждого визуального кейса. Укажите версию
exteraless из **Настройки → О программе** и версию Botile из
**Настройки → Плагины → Botile**.

## Expected load log / Ожидаемый журнал загрузки

```text
Botile 1.1.0 starting (installed metadata version=1.1.0)
diag hooks permission=True
diag sdk=...
hook bind: installed ImageReceiver.setForUserOrChat
hook radius: installed ImageReceiver.setRoundRadius(int[])
hook image: installed ImageReceiver.setImage core
hook bitmap: installed ... setImageBitmap overload(s)
hook dialog: installed DialogCell.update fallback
Botile hooks: bind=OK radius=... image=... dialog=...
diag native_hooks ready=True broken=False
```

If `bind`, `radius`, or `image` is `FAILED`, stop that case and report the exact
line. If `hooks permission=False`, grant the permission before any visual test.

Если `bind`, `radius` или `image` — `FAILED`, остановите кейс и пришлите точную
строку. Если `hooks permission=False`, выдайте разрешение до визуальных тестов.

## Test cases / Тестовые кейсы

### 1. Load and version / Загрузка и версия

- [ ] Botile 1.1.0 appears in the plugin list.
- [ ] The log contains `Botile 1.1.0 starting (installed metadata version=1.1.0)`.
- [ ] `diag hooks permission=True`.
- [ ] `diag sdk` shows the actual SDK.
- [ ] `diag native_hooks ready=True broken=False`.

- [ ] Botile 1.1.0 виден в списке плагинов.
- [ ] В журнале есть `Botile 1.1.0 starting (installed metadata version=1.1.0)`.
- [ ] `diag hooks permission=True`.
- [ ] `diag sdk` показывает фактический SDK.
- [ ] `diag native_hooks ready=True broken=False`.

### 2. Main dialog list / Основной список чатов

Prepare one bot chat, one regular user, one group, one channel. Take a
screenshot of the list.

Подготовьте чат с ботом, обычным пользователем, группой и каналом. Сделайте
скриншот списка.

- [ ] The bot avatar is a rounded square.
- [ ] The regular user avatar keeps its previous shape (normally a circle).
- [ ] The group avatar is unchanged.
- [ ] The channel avatar is unchanged.
- [ ] The log shows `diag first bind ... bot=true` for the bot.
- [ ] The log shows `diag first bot detected`.
- [ ] The log shows a radius verification such as
      `diag radius verified in receiver after ...`.

- [ ] Аватар бота — скруглённый квадрат.
- [ ] Аватар обычного пользователя сохраняет прежнюю форму (обычно круг).
- [ ] Аватар группы не изменён.
- [ ] Аватар канала не изменён.
- [ ] В журнале есть `diag first bind ... bot=true` для бота.
- [ ] В журнале есть `diag first bot detected`.
- [ ] В журнале есть подтверждение радиуса, например
      `diag radius verified in receiver after ...`.

### 3. Recycling / Переработка ячеек

Scroll rapidly so that a dialog cell is reused: bot → user → bot and
bot → group → bot. Stop on each state and check.

Быстро прокрутите список так, чтобы ячейка переиспользовалась: бот →
пользователь → бот и бот → группа → бот. Остановитесь на каждом состоянии.

- [ ] A recycled cell showing a regular user is circular/unchanged.
- [ ] A recycled cell showing a group/channel is unchanged.
- [ ] A recycled cell showing a bot is a rounded square again.
- [ ] No cell keeps the previous occupant's shape.
- [ ] Scrolling remains smooth; the summary shows non-zero `binds` and
      `overrides` and no repeated error flood.

- [ ] Переиспользованная ячейка с обычным пользователем круглая/не изменена.
- [ ] Переиспользованная ячейка с группой/каналом не изменена.
- [ ] Переиспользованная ячейка с ботом снова является скруглённым квадратом.
- [ ] Ни одна ячейка не сохраняет форму предыдущего собеседника.
- [ ] Прокрутка остаётся плавной; в сводке ненулевые `binds` и `overrides`, нет
      потока повторяющихся ошибок.

### 4. Private bot chat / Личный чат с ботом

Open a chat with a bot.

Откройте чат с ботом.

- [ ] The bot avatar in the chat header is a rounded square.
- [ ] Bot message sender avatars are rounded squares.
- [ ] The log reports `bot=true` and radius verification for these receivers.

- [ ] Аватар бота в шапке чата — скруглённый квадрат.
- [ ] Аватары отправителя-бота в сообщениях — скруглённые квадраты.
- [ ] Журнал сообщает `bot=true` и подтверждение радиуса для этих получателей.

### 5. Group chat / Групповой чат

Open a group containing a bot and regular users.

Откройте группу, где есть бот и обычные пользователи.

- [ ] Bot sender avatars are rounded squares.
- [ ] Regular-user sender avatars keep their shape.
- [ ] The group header avatar is unchanged.
- [ ] The group avatar in the chat list is unchanged.

- [ ] Аватары отправителя-бота — скруглённые квадраты.
- [ ] Аватары обычных пользователей сохраняют форму.
- [ ] Аватар группы в шапке не изменён.
- [ ] Аватар группы в списке чатов не изменён.

### 6. Search results / Результаты поиска

Search for a bot in the chat list search.

Найдите бота через поиск в списке чатов.

- [ ] The bot avatar in the search result is a rounded square.
- [ ] Regular users/channels in search keep their shapes.
- [ ] The log shows a direct avatar path or the normal bind path for the result.
- [ ] If the log prints `direct avatar parent not covered: ...`, save the class
      name and report it; that surface is not covered.

- [ ] Аватар бота в результате поиска — скруглённый квадрат.
- [ ] Обычные пользователи/каналы в поиске сохраняют форму.
- [ ] Журнал показывает прямой путь аватара или обычный путь привязки.
- [ ] Если в журнале `direct avatar parent not covered: ...`, сохраните имя
      класса и пришлите его; эта поверхность не покрыта.

### 7. Bot profile / Профиль бота

Open the profile of a bot with a normal profile photo.

Откройте профиль бота с обычным фото профиля.

- [ ] The profile avatar is a rounded square.
- [ ] The avatar of a regular user profile is unchanged.
- [ ] The log reports a direct avatar or a bind for the profile.
- [ ] If the bot uses a vector/video profile avatar, record that separately; the
      current implementation may not cover that path.

- [ ] Аватар в профиле — скруглённый квадрат.
- [ ] Аватар обычного пользователя в профиле не изменён.
- [ ] Журнал сообщает прямой путь или привязку для профиля.
- [ ] Если у бота векторный/видео-аватар, отметьте отдельно; текущая
      реализация может не покрывать этот путь.

### 8. Reply and forward previews / Превью ответов и пересылок

Open a chat with a forwarded message from a bot and a reply preview containing
a bot.

Откройте чат с пересланным сообщением от бота и превью ответа с ботом.

- [ ] The mini avatar next to the forwarded name is a rounded square.
- [ ] The mini avatar in the reply preview is a rounded square.
- [ ] Regular-user mini avatars keep their shape.
- [ ] The log shows a bot bind for the `AvatarSpan` receiver.

- [ ] Мини-аватар рядом с именем пересланного сообщения — скруглённый квадрат.
- [ ] Мини-аватар в превью ответа — скруглённый квадрат.
- [ ] Мини-аватары обычных пользователей сохраняют форму.
- [ ] Журнал показывает привязку бота для получателя `AvatarSpan`.

### 9. Account switch / Переключение аккаунта

Switch between two accounts with different dialogs.

Переключитесь между двумя аккаунтами с разными диалогами.

- [ ] Bot avatars in the second account are rounded squares.
- [ ] Regular users/groups/channels are unchanged.
- [ ] No bot shape leaks onto a regular user after switching.

- [ ] Аватары ботов во втором аккаунте — скруглённые квадраты.
- [ ] Обычные пользователи/группы/каналы не изменены.
- [ ] После переключения форма бота не «протекает» на обычного пользователя.

### 10. Disable / restore / Выключение и восстановление

Disable Botile while the dialog list is visible, then enable it again.

Выключите Botile при открытом списке чатов, затем включите снова.

- [ ] On disable, visible bot avatars return to the normal radius without
      restarting.
- [ ] On enable, bots become rounded squares after the next normal
      bind/update/scroll.
- [ ] The unload log contains a summary and no hook errors.
- [ ] Regular users/groups/channels remain unchanged throughout.

- [ ] При выключении видимые аватары ботов возвращаются к обычному радиусу без
      перезапуска.
- [ ] При включении боты становятся скруглёнными квадратами после следующей
      привязки/обновления/прокрутки.
- [ ] Журнал выгрузки содержит сводку и не содержит ошибок хуков.
- [ ] Обычные пользователи/группы/каналы не меняются.

### 11. Custom images / Пользовательские изображения

Check a custom dialog avatar (for example, the archive/folder cell or Saved
Messages) after a bot cell.

Проверьте пользовательский аватар диалога (например, архив/папку или
«Избранное») после ячейки с ботом.

- [ ] The custom image is not turned into a bot avatar.
- [ ] The log may show `first custom image on marked receiver`.
- [ ] A regular user/group row after the custom row keeps its shape.

- [ ] Пользовательское изображение не превращается в аватар бота.
- [ ] В журнале может быть `first custom image on marked receiver`.
- [ ] Обычный пользователь/группа после этой строки сохраняют форму.

## Pass criteria / Критерии прохождения

A step passes only when both the log and the screenshot agree. A step is failed
if the log has `binds=0`, `bots=0`, `overrides=0`, a hook registration failure,
a `not stuck` radius, or the screenshot shows a circle for a bot / a square for a
non-bot.

A visual change in one case does not prove the other surfaces. Report each case
separately.

Шаг считается пройденным только если журнал и скриншот совпадают. Шаг не
пройден, если в журнале `binds=0`, `bots=0`, `overrides=0`, ошибка регистрации
хука, `not stuck` радиуса, или на скриншоте круг у бота / квадрат у не-бота.

Визуальное изменение в одном кейсе не доказывает остальные поверхности.
Сообщайте о каждом кейсе отдельно.

## Report template / Шаблон отчёта

```text
exteraless version / версия exteraless:
Botile version / версия Botile:
SDK / SDK:
Device / устройство:
Android / Android:
Hooks permission / разрешение hooks:
Native hooks ready / нативные хуки:
Cases passed / пройденные кейсы:
Cases failed / непройденные кейсы:
Screenshots attached / скриншоты:
Log file attached / файл журнала:
Notes / примечания:
```

## Failure decision tree / Дерево диагностики

| Log / Журнал | Meaning / Значение |
|---|---|
| no start line / нет строки запуска | not loaded/enabled or old file / не загружен, не включён или старый файл |
| `hooks permission=False` | grant hooks and re-enable / выдайте hooks и включите заново |
| `native_hooks ready=False broken=True` | native hook init disabled/broken; restart/reinstall client / нативные хуки отключены или сломаны; перезапустите/переустановите клиент |
| `hook bind: FAILED` | registration/reflection failed; send exact line / ошибка регистрации/reflection; пришлите строку |
| `binds=0` | bind hook not invoked; send full log/build / хук не вызывается; пришлите журнал и сборку |
| `binds>0`, `bots=0` | entity not detected as bot; send first-bind class/id / сущность не определяется как бот; пришлите класс/id из first bind |
| `bots>0`, `overrides=0` | radius filter/hook did not run / фильтр или хук радиуса не сработал |
| `radius ... did not stick` | later overwrite or build difference / перезапись позже или отличие сборки |
| `direct avatar parent not covered` | uncovered direct surface; send class name / неизвестная поверхность; пришлите класс |
| verified but no visual / подтверждено, но визуально нет | draw/clip path issue; send parent class and screenshot / проблема отрисовки/обрезки; пришлите класс и скриншот |

Do not publish or create a release from this validation; attach the results to
the local audit.

Не публикуйте и не создавайте релиз по результатам этой проверки; приложите
результаты к локальному аудиту.
