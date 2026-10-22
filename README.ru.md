# Botile

[![CI](https://github.com/iamvxrn/Botile/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/iamvxrn/Botile/actions/workflows/ci.yml)
[![Release](https://github.com/iamvxrn/Botile/actions/workflows/release.yml/badge.svg)](https://github.com/iamvxrn/Botile/actions/workflows/release.yml)
[![GitHub Releases](https://img.shields.io/badge/releases-GitHub-2f81f7)](https://github.com/iamvxrn/Botile/releases)

**Дайте ботам отдельную форму аватара.**

[История](CHANGELOG.md) · [Участие](CONTRIBUTING.md) · [Безопасность](SECURITY.md) · [Проверка](VALIDATION.md)

Версия **1.1.3**. Botile рисует аватары Telegram-ботов как скруглённые
квадраты с тонкой адаптивной обводкой, не меняя форму аватаров обычных
пользователей, групп, каналов и пользовательских изображений.

## Установка и обновление

1. Из опубликованного релиза скачайте `Botile-<version>.plugin` и проверьте его
   по `SHA256SUMS`; ассет побайтово совпадает с `Botile.plugin`. Для этого
   checkout установите `Botile.plugin` напрямую. Устанавливайте поверх
   существующей установки Botile. Если клиент оставил старый файл, удалите
   Botile и установите этот файл заново.
2. В окне установки отметьте **Java hooks (full control)**. Без разрешения
   `hooks` плагин не может менять Java-представления и останется неактивным.
3. Включите Botile.
4. Убедитесь, что загружен именно файл 1.1.3. Начало журнала плагина:

   ```text
   Botile 1.1.3 starting (installed metadata version=1.1.3)
   ```

Плагин не требует root, LSPosed, модификации APK, сети или дополнительных
Python-пакетов. Единственное объявленное разрешение — `hooks`; exteraless
реализует его через встроенный Aliuhook.

### Диапазон версий

Минимальные значения метаданных соответствуют проверенной сборке и API:

- `__app_version__ = ">=12.10.6"`
- `__sdk_version__ = ">=1.4.5.3"`

Те же классы, методы и сигнатуры были проверены в текущем исходнике
(`13.0.2`, SDK `1.4.5.7`), поэтому этот диапазон совместим по исходному коду.
Более старый ориентир из документации (`12.5.1` / SDK `1.4.4.3`) для точной
поверхности хуков и фильтров этого плагина **не проверялся**, поэтому Botile
его не заявляет. Это утверждение о метаданных и исходниках, а не доказательство
правильной отрисовки на телефоне.

## Релизы и проверка

Опубликованные сборки прикреплены к [GitHub Releases](https://github.com/iamvxrn/Botile/releases):

- `Botile-<version>.plugin` — устанавливаемый ассет, побайтово совпадающий с
  `Botile.plugin` из тега;
- `SHA256SUMS` содержит его SHA-256; перед установкой выполните
  `sha256sum -c SHA256SUMS`.

Workflow `Release` запускается только для существующего тега
`vMAJOR.MINOR.PATCH`, заново выполняет проверки CI, требует точного совпадения
тега с `__version__` и публикует сгенерированные release notes. Он не создаёт и
не перемещает теги; порядок ревью описан в [CONTRIBUTING.md](CONTRIBUTING.md).

Исходного коммита или релиза 1.1.2 нет. Статус релизов и история исходников
записаны в [CHANGELOG.md](CHANGELOG.md).

## Что изменилось с 1.0

Версия 1.0 не проверялась на устройстве. Она устанавливалась, но визуально
ничего не меняла; при успешной загрузке в журнал попадала только строка
`Botile active`.

Был изучен фактический APK exteraless, найденный на этой машине:

- APK: `exteraless-v12.10.6-00c14f4(1261).apk`
- package: `com.exteraless.app`
- версия приложения: `12.10.6-00c14f4`
- версия SDK плагинов: `1.4.5.3`
- Python: `3.11`

В APK присутствуют все цели, которые использовала 1.0:

- `org.telegram.ui.Cells.DialogCell.update(int, boolean)` — `(I Z)Z`
- `DialogCell.avatarImage: ImageReceiver` (public)
- `DialogCell.user: TLRPC.User` (private)
- `DialogCell.customDialog` (private)
- `ImageReceiver.setRoundRadius(int)` — `(I)V`
- `ImageReceiver.setRoundRadius(int[])` — `([I)V`
- `ImageReceiver.setAvatarCornersApplied(boolean)` — `(Z)V`
- `TLRPC$User.bot` (public boolean)

То есть сбой 1.0 — **не** выдуманный класс, метод, поле или отказ по версии.
Это был тихий сбой во время выполнения. Снаружи одинаково выглядели несколько
причин:

1. разрешение `hooks` не выдано / плагин не получил доверенный уровень;
2. нативная инициализация хуков отключена или сломана;
3. хук зарегистрирован, но не вызывается;
4. приватное поле читалось через reflection и возвращало `None`;
5. радиус применялся, но позже перезаписывался.

В 1.0 не было журнала вызовов, определения сущности и проверки радиуса,
поэтому на практике сбой был молчаливым. В 1.1.0 полностью убрана зависимость
от приватного поля и добавлены журналы регистрации хуков, первого вызова,
определения бота, переопределения радиуса, обратного чтения радиуса, очистки
пользовательских изображений и ошибок. **Для подтверждения визуального
результата по-прежнему нужен журнал с реального Android-устройства.**

## История запуска и обводка в 1.1.3

Журнал 1.1.0 с устройства на exteraless 12.10.6 (`00c14f4`) показал, что запуск
останавливался до регистрации хуков: у прокси класса не было метода
`getDeclaredMethod()`. В 1.1.1 вызов заменили на `getDeclaredMethods()`, но это
тоже метод экземпляра `java.lang.Class`, а не метода прокси, который возвращает
`find_class()` (`java.jclass(...)`). Проверка точного SDK подтверждает: SDK сам
нормализует прокси через `hook_utils._as_class()` до `java.lang.Class`, и
`BasePlugin.hook_method()` использует этот помощник.

В 1.1.2 прокси сначала нормализуется, затем выбирается точная перегрузка, и
готовый `Method` передаётся в `hook_method()`. Пользователь сообщает, что 1.1.2
работает. В 1.1.3 этот путь сохранён и добавлена необязательная адаптивная
обводка, описанная ниже. Сама обводка ещё не проверена на телефоне.

## Матрица покрытия

| Поверхность | Реализация | Статус |
|---|---|---|
| Основной список чатов | `ImageReceiver.setForUserOrChat` + `setRoundRadius`; fallback в `DialogCell.update` | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Результаты поиска на `DialogCell` | Те же центральные хуки + fallback | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Результаты поиска на `ProfileSearchCell` | Прямой `ImageReceiver.setImage(..., parentObject=user/chat, ...)` + список родительских классов | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Аватары отправителей в личных/групповых чатах (`ChatMessageCell`) | Центральные хуки | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Списки участников и окна «Поделиться» (`UserCell`, `ShareDialogCell`, `HintDialogCell`) | Центральные хуки | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Аватар в шапке чата (`ChatAvatarContainer`) | Центральные хуки | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Профиль бота, обычное фото (`ProfileActivity$AvatarImageView`) | Прямой `setImage` + разрешённый родительский класс + хук радиуса | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Профиль бота, обычное фото (`ProfileActivity2$AvatarImage`) | То же | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Превью ответов и мини-аватары пересланных сообщений (`AvatarSpan`) | Центральные хуки | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Прочие виджеты с `ImageReceiver.setForUserOrChat` | Центральные хуки | Реализовано; исходник просмотрен; телефонная проверка ожидается |
| Тонкая обводка бота | after-хук `ImageReceiver.draw(Canvas, BackgroundThreadDrawHolder)`, фильтр по метке, адаптивный цвет темы | Реализовано; исходник/моки проверены; телефонная проверка ожидается |
| Векторный/видео-аватар профиля бота через `setImageBitmap` | В этой точке вызова нет TLRPC-сущности | **Надёжно не покрыто**; ограничение |
| Полноэкранный просмотр фото | Намеренно исключён (это не аватар) | Не покрыто по замыслу |
| Уведомления и отрисовка вне UI | Нет пути аватара через `ImageReceiver` | Не покрыто |

## Как это работает

### 1. Хук привязки

```text
ImageReceiver.setForUserOrChat(TLObject, Drawable, Object, boolean, int, boolean)
```

After-хук читает фактический `TLRPC.User`/`TLRPC.Chat`. Если это пользователь
с `bot == true`, получатель помечается в публичном поле `mark`, а **полный
радиус всех четырёх углов** (включая `0,0,0,0` и асимметричные значения)
сохраняется в `java.util.WeakHashMap`. Предыдущий объект `mark` сначала
запоминается; он восстанавливается только если получатель всё ещё несёт метку
Botile. Слабые ключи не удерживают ячейки диалогов и получателей изображений.

### 2. Хук радиуса

```text
ImageReceiver.setRoundRadius(int[])
```

Java-фильтр вызывает Python только для получателей с меткой Botile. Хук:

- копирует запрошенный приложением радиус всех четырёх углов как базовый для
  восстановления;
- принудительно ставит радиус Botile на все четыре угла;
- передаёт управление оригинальному методу;
- после вызова читает радиус обратно и пишет в журнал, применился ли он.

Восстановление передаёт сохранённый `int[4]` обратно в `setRoundRadius(int[])`,
поэтому нулевые и асимметричные углы не сплющиваются. Восстановление `mark`
защищено: метка, поставленная кем-то другим после Botile, не перезаписывается.

Именно это не даёт перезаписать радиус тем, кто вызывает `setRoundRadius`
**после** `setForUserOrChat` (так делает `DialogCell.update`).

Максимальный радиус — 11 dp, как требует список чатов. Для очень маленьких
аватаров он уменьшается пропорционально, чтобы мини-аватар 18 dp не стал
кругом:

```text
radius_px = round(avatar_width_px * 0.22), но не больше 11 dp
```

### 3. Пользовательские изображения

`ImageReceiver.setImage(...)` и `setImageBitmap(...)` фильтруются по той же
метке. Когда пользовательское/не-сущностное изображение заменяет аватар бота,
Botile восстанавливает сохранённый радиус и снимает метку. Вызовы внутри
`setForUserOrChat` пропускаются через thread-local счётчик глубины: ими
занимается after-хук привязки.

### 4. Прямые аватары через setImage

Профили и `ProfileSearchCell` не используют `setForUserOrChat`; они вызывают
`ImageReceiver.setImage(..., parentObject=user/chat, ...)`. Botile имеет
Java-фильтр для `TLRPC.User`/`TLRPC.Chat` в аргументе 9, затем проверяет
класс родителя получателя:

```text
org.telegram.ui.ProfileActivity$AvatarImageView   (включая $1 и другие подклассы)
org.telegram.ui.ProfileActivity2$AvatarImage
org.telegram.ui.Cells.ProfileSearchCell
```

Меняются только эти известные контейнеры аватаров. Неизвестные контейнеры с
ботом логируются один раз с именем класса, а не изменяются вслепую.

### 5. Fallback списка чатов

`DialogCell.update(int, boolean)` по-прежнему перехватывается after-хуком, но
радиус повторно применяется только если `avatarImage` имеет метку Botile. Это
небольшая страховка для основного списка; приватные поля `DialogCell` больше
не используются.

### 6. Обводка аватара (1.1.3)

Botile может добавить тонкую обводку тем же помеченным получателям, не заменяя
изображение, view или путь радиуса:

```text
ImageReceiver.draw(Canvas, BackgroundThreadDrawHolder)   (after-хук)
```

Хук фильтруется по метке Botile, поэтому обычные пользователи, группы и каналы
вообще не попадают в Python. Обводка пропускается, если `draw()` вернул false,
если это фоновая отрисовка (non-null holder) или если alpha получателя равна
нулю. Она рисуется **внутри** границ изображения, повторяет текущий радиус
углов и поэтому не может увеличить или обрезать layout аватара.
Фоновые draw-вызовы с non-null holder пропускаются, чтобы не трогать Canvas
вне UI-потока.

Цвет не хардкодится:

```text
Theme.getColor(Theme.key_windowBackgroundWhiteBlackText)
Theme.multAlpha(color, 0.45 * avatarAlpha)
```

Это адаптивный контрастный цвет текста (чёрный в светлой теме, белый в тёмной).
Штрих 1 dp с alpha 45% достаточно тонкий, но отделяет аватар бота от похожего
фона Telegram. `Paint` и `RectF` создаются один раз и переиспользуются. Если
`Paint`, `Theme` или draw-хук не устанавливаются, плагин пишет
`hook border: ...` / `diag border disabled` и продолжает работать с радиусом;
рендерер не подменяется, плагин не становится неактивным.

Обводка использует глобальный цвет темы, а не per-chat `ResourcesProvider`.
Пользовательские темы чата могут дать немного другой акцент, но обводка
остаётся читаемой в светлой и тёмной темах.

### Переработка, аккаунты, выгрузка

- При повторной привязке `DialogCell` и ячеек сообщений снова вызывается
  `setForUserOrChat`, который обновляет метку и базовый радиус.
- Бот → обычный пользователь/группа/канал: восстанавливается сохранённый
  радиус.
- Обычный пользователь → бот: ставится радиус бота.
- Определение бота идёт по сущности получателя, а не по выбранному аккаунту.
- При выгрузке все хуки снимаются, а все отслеживаемые получатели
  восстанавливаются на UI-потоке.

## Диагностика и проверка на телефоне

Плагин пишет через `self.log` в журнал плагинов exteraless (`PluginLog` /
`FileLog`, префикс `[plugin:botile]`).

Сбор журнала:

```bash
adb logcat -c
# открыть основной список чатов, прокрутить ботов/пользователей/группы/каналы,
# открыть чат с ботом и профиль бота
adb logcat -d -v time | grep -i "botile"
```

Также смотрите встроенный журнал: **Настройки → Плагины → Botile → журнал**.

Ожидаемая успешная последовательность:

```text
Botile 1.1.3 starting (installed metadata version=1.1.3)
diag hooks permission=True
diag sdk=1.4.5.3
hook bind: installed ImageReceiver.setForUserOrChat
hook radius: installed ImageReceiver.setRoundRadius(int[])
hook image: installed ImageReceiver.setImage core
hook border: installed ImageReceiver.draw outline
hook bitmap: installed ... setImageBitmap overload(s)
hook dialog: installed DialogCell.update fallback
Botile hooks: bind=OK radius=OK image=OK border=OK dialog=OK
diag first bind: entity=... bot=true parent=...
diag first bot detected: ...
diag radius verified in receiver ...
diag first radius override: requested=... parent=... -> ...px
```

При прокрутке должны появляться сводки:

```text
diag periodic: binds=500 bots=... nonbots=... overrides=... verified=... clears=...
```

### Дерево диагностики

| Что в журнале | Значение / действие |
|---|---|
| Нет `Botile 1.1.3 starting` | Плагин не загружен/не включён или установлен старый файл. Переустановите и проверьте **Плагины → Botile**. |
| `diag hooks permission=False` | Выдайте разрешение **hooks**, затем выключите и включите Botile. |
| `diag native_hooks ready=False broken=True` | Exteraless отключил нативные хуки после сбоя. Перезапустите/переустановите клиент и очистите состояние сбоя нативных хуков движка; без Aliuhook плагин не работает. |
| `hook bind: FAILED ...` | Среда отклонила метод или не смогла получить его. В журнале будет метод и исключение. |
| `binds=0` после прокрутки и открытия чатов | Хук установлен, но не вызывается. Приложите полный журнал и точную сборку exteraless. |
| `binds>0`, `bots=0` | Хук вызывается, но сущность не определяется как бот. Приложите первую строку `first bind` с классом/id. |
| `bots>0`, `overrides=0` | Фильтр радиуса не сработал или хук радиуса не установился. Ищите ошибки `HookFilter` и строки установки хуков. |
| `diag radius override did not stick` | Метод выполнился, но радиус прочитался другим. Это указывает на перезапись позже или отличие сборки. |
| `hook border: FAILED ...` / `diag border disabled: ...` | Необязательную обводку не удалось установить; радиус продолжает работать. Пришлите точную строку, тему и сборку. |
| `diag direct avatar parent not covered: ...` | Прямой аватар на неизвестном контейнере. Пришлите имя класса; можно добавить точечный хук. |
| `overrides>0`, `verified>0`, но визуально ничего | Значение в получателе правильное, но путь отрисовки/обрезки его не учитывает. Нужен скриншот и класс родителя. |

**Android-журнал для 1.1.0 уже есть:** он подтверждает, что регистрация хука
сорвалась при поиске метода. 1.1.1 не проверялась на устройстве и опиралась на
то же неверное предположение о прокси; в 1.1.3 прокси нормализуется перед
reflection. Журнала для 1.1.3 пока нет. Статический анализ и моки не доказывают
результат отрисовки: считать проблему решённой можно после журнала с
установленными хуками и `binds>0`, `bots>0`, `overrides>0`, `verified>0`, а
также скриншота с квадратными аватарами ботов и круглыми аватарами обычных
пользователей.

Подробный двуязычный протокол проверки: [VALIDATION.md](VALIDATION.md).

## Выполненная проверка

### Фактически выполнено здесь

- Синтаксис Python компилируется (`python3` 3.14 на хосте; исходник совместим
  с Python 3.11 приложения).
- Метаданные разобраны фактическим AST-парсером exteraless:
  `id=botile`, `name=Botile`, описание, `version=1.1.3`,
  `permissions=["hooks"]`, без зависимостей.
- Фактический сканер возможностей exteraless: только `hooks`, без сети,
  файлов и сообщений.
- `python3 tests/test_state_preservation.py` прошёл: 16 хостовых тестов.
  Они проверяют нормализацию runtime-прокси класса (`getClass()` →
  `java.lang.Class`), выбор точной перегрузки через `getDeclaredMethods()`,
  точные сигнатуры bind и DialogCell через runtime-прокси, отсутствие нужной
  перегрузки, восстановление нулевых и асимметричных
  радиусов, сохранение исходного и последующего внешнего `mark`, а также
  рамку: только для помеченных ботов, внутри bounds, по радиусу, с адаптивным
  цветом темы и без отрисовки для прозрачных/фоновых/неудачных кадров.
- Моки проверяют выбор метода, восстановление состояния и математику отрисовки
  обводки. Они не запускают callbacks Aliuhook и не проверяют отрисовку Android.

### Проверено статически по исходникам/APK

- APK `12.10.6-00c14f4(1261)`: SDK `1.4.5.3`; методы, поля, перегрузки
  `setForUserOrChat`, сигнатура core `setImage` и `setRoundRadius(int[])`
  существуют.
- API обводки есть в точном APK: `ImageReceiver.draw(Canvas,
  BackgroundThreadDrawHolder)`, `getImageX/Y/Width/Height()`,
  `getRoundRadius()`, `getAlpha()`, `getCurrentAlpha()`,
  `Theme.key_windowBackgroundWhiteBlackText`, `Theme.getColor(int)` и
  `Theme.multAlpha(int, float)`.
- Исходник GitHub `00c14f4`: `DialogCell.update` вызывает
  `setAvatarCornersApplied(true)`, затем `setRoundRadius(...)`, а аватар
  задаётся через `setForUserOrChat` или прямой `setImage` с сущностью в
  `parentObject`.
- Проверены пути `ProfileActivity$AvatarImageView`,
  `ProfileActivity2$AvatarImage`, `ProfileSearchCell`, `AvatarSpan`.
- Проверены жизненный цикл плагина, ключ разрешения, поддержка
  `HookFilter` condition/or и формат установки `.plugin` в исходниках
  exteraless.

### Требует реального Android-устройства

Всё визуальное остаётся непроверенным на телефоне:

- фактическая отрисовка и форма углов;
- плавность прокрутки и переработки;
- переключение аккаунтов;
- восстановление при выключении/включении;
- профили, шапки, пересылки;
- инициализация нативного Aliuhook.

## Ограничения

- Векторные/видео-аватары профиля бота, задаваемые прямым
  `setImageBitmap(...)`, не имеют TLRPC-сущности в точке вызова. Обычные фото
  профиля покрыты; векторный путь не гарантирован.
- Полноэкранный просмотр фото и уведомления намеренно не являются целями.
- Включение Botile на уже отрисованном экране не вызывает глобальную
  перезагрузку списка. Ячейки обновятся при следующей привязке/обновлении;
  это сделано, чтобы не требовать лишних разрешений и не дёргать UI.
- Для не-ботов сохраняется текущая настройка скругления клиента. Если она уже
  скругляет всех, Botile её не переопределяет.
- Радиус ограничен 11 dp и уменьшается для маленьких аватаров; у профилей
  поэтому максимум 11 dp, а не большой пропорциональный радиус.
- Плагину нужны разрешение `hooks` и доверенный уровень. В изолированном или
  ограниченном режиме без хуков он не работает.
- Будущие изменения клиента будут видны в диагностическом журнале, а не
  приведут к молчаливому отсутствию эффекта.

## Ссылки на исходники

Проверено по:

- APK `exteraless-v12.10.6-00c14f4(1261).apk`
  (`com.exteraless.app`, SDK `1.4.5.3`, Python 3.11);
- GitHub `exteraless/exteraless`, коммит
  [`00c14f4`](https://github.com/exteraless/exteraless/commit/00c14f4),
  соответствующий строке версии APK;
- текущий main `8b7ec40` — где это относится к делу.

Ключевые файлы/классы:

| Файл | Что проверено |
|---|---|
| `TMessagesProj/src/main/java/org/telegram/messenger/ImageReceiver.java` | `setForUserOrChat(...)`, core 11-arg `setImage(...)`, `setRoundRadius(int[])`, `draw(Canvas, BackgroundThreadDrawHolder)`, `getImageX/Y/Width/Height()`, `getRoundRadius()`, `getAlpha()`, `getCurrentAlpha()`, `setAvatarCornersApplied()`, `setMark/getMark` |
| `TMessagesProj/src/main/java/org/telegram/ui/ActionBar/Theme.java` | `key_windowBackgroundWhiteBlackText`, `getColor(int)`, `multAlpha(int, float)` для адаптивной обводки |
| `TMessagesProj/src/main/java/org/telegram/ui/Cells/DialogCell.java` | `avatarImage`, `update(int, boolean)`, установка радиуса через `setRoundRadius` |
| `TMessagesProj/src/main/java/org/telegram/tgnet/TLRPC.java` | `TLRPC.User.bot` |
| `TMessagesProj/src/main/java/org/telegram/ui/Cells/ProfileSearchCell.java` | прямой `setImage(..., parentObject=user/chat, ...)` и радиус аватара |
| `TMessagesProj/src/main/java/org/telegram/ui/ProfileActivity.java` | прямой путь `ProfileActivity$AvatarImageView` |
| `TMessagesProj/src/main/java/org/telegram/ui/ProfileActivity2.java` | прямой путь `ProfileActivity2$AvatarImage` |
| `TMessagesProj/src/main/java/org/telegram/ui/AvatarSpan.java` | мини-аватары пересылок/ответов используют `setForUserOrChat` |
| `TMessagesProj/src/main/java/app/exteraless/plugins/xposed/HookFilter.java` | Java-фильтры `condition`, `or`, `argument_is_instance_of` |
| `TMessagesProj/src/main/java/app/exteraless/plugins/PluginPermissions.java` | разрешение `hooks` |
| `TMessagesProj/src/main/python/base_plugin.py` | `MethodHook`, `HookFilter`, `hook_method`, жизненный цикл |
| `TMessagesProj/src/main/python/hook_utils.py` | `find_class` возвращает прокси класса Chaquopy; `_as_class` нормализует его в `java.lang.Class` перед reflection. Приватный reflection из 1.0 больше не используется |

## Файлы

- `Botile.plugin` — устанавливаемый плагин (Python-исходник с метаданными),
  версия 1.1.3.
- `README.md` — английская документация.
- `README.ru.md` — эта русская документация.
- `CHANGELOG.md` — двуязычная история исходников и релизов.
- `CONTRIBUTING.md` — двуязычный порядок участия, проверки, тегов и релизов.
- `SECURITY.md` — двуязычная политика приватного сообщения об уязвимостях.
- `VALIDATION.md` — двуязычный протокол проверки на телефоне.
- `.gitignore` — игнорирует Python-кэши, `dist/`, virtualenv и файлы редакторов.
- `.github/workflows/ci.yml` — read-only проверки для PR/main/ручного запуска.
- `.github/workflows/release.yml` — проверка, сборка и публикация GitHub Release
  по тегу.
- `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`,
  `.github/dependabot.yml` — формы issue/PR и обновления закреплённых Actions.
- `scripts/package_release.py` — stdlib-валидация метаданных и сборка релиза.
- `tests/test_state_preservation.py` — хостовые mock-тесты состояния радиуса,
  `mark` и обводки (нулевые и асимметричные углы, бот → не-бот, выгрузка,
  сохранение метки).
