<p align="center">
  <img src="assets/github-banner.svg" alt="VantaVault GitHub Banner" width="100%">
</p>

<h1 align="center">VantaVault</h1>

<p align="center">
  <strong>Локальный desktop-vault для внешнего диска.</strong><br>
  Автоматически замечает подключение целевого носителя, открывает рабочее пространство,
  держит вход под локальной защитой и дает AES-архивы без облака и без лишней магии.
</p>

<p align="center">
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/mitaro-cs/VantaVault?display_name=tag&style=for-the-badge&label=latest%20release&color=F3F4F6&labelColor=111111">
  </a>
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Download" src="https://img.shields.io/badge/Download-Releases-F3F4F6?style=for-the-badge&labelColor=111111">
  </a>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-F3F4F6?style=for-the-badge&labelColor=111111">
  <img alt="Contributions Welcome" src="https://img.shields.io/badge/Contributions-Welcome-F3F4F6?style=for-the-badge&labelColor=111111">
  <img alt="macOS" src="https://img.shields.io/badge/macOS-supported-F3F4F6?style=for-the-badge&logo=apple&logoColor=111111&labelColor=111111">
  <img alt="Windows" src="https://img.shields.io/badge/Windows-supported-F3F4F6?style=for-the-badge&logo=windows&logoColor=111111&labelColor=111111">
  <img alt="pywebview" src="https://img.shields.io/badge/pywebview-desktop%20shell-F3F4F6?style=for-the-badge&labelColor=111111">
  <img alt="AES" src="https://img.shields.io/badge/AES-local%20archives-F3F4F6?style=for-the-badge&labelColor=111111">
</p>

<p align="center">
  <a href="#обзор">Обзор</a> ·
  <a href="#ключевые-сценарии">Ключевые сценарии</a> ·
  <a href="#скачать">Скачать</a> ·
  <a href="#для-открытого-репозитория">Open Source</a> ·
  <a href="#как-помочь">Как помочь</a> ·
  <a href="#локальный-запуск">Локальный запуск</a> ·
  <a href="#сборка-релизов">Сборка релизов</a> ·
  <a href="#безопасность">Безопасность</a> ·
  <a href="#лицензия">Лицензия</a>
</p>

## Обзор

`VantaVault` решает очень конкретную задачу: держать внешний диск в контролируемом,
локальном и удобном desktop-потоке. Приложение следит за подключением нужного тома,
помогает быстро открыть его, хранит локальные настройки по умолчанию и добавляет
AES-архивирование прямо в рабочий интерфейс.

> Диск появился -> приложение это заметило -> пользователь вошел локальным паролем -> vault открылся -> при необходимости данные ушли в зашифрованный архив.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>Auto Presence</h3>
      <p>Приложение понимает, подключен ли целевой диск <code>VantaVault</code>, и умеет автоматически смещать фокус на него.</p>
    </td>
    <td width="50%" valign="top">
      <h3>Local Security</h3>
      <p>Вход защищен локальным паролем, PBKDF2-хешем, сессией и временным <code>lockout</code> после серии неверных попыток.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>Default Settings</h3>
      <p>Есть отдельный экран настроек: целевой диск, автооткрытие, уведомления, лимит попыток и параметры AES-архивов.</p>
    </td>
    <td width="50%" valign="top">
      <h3>Recovery Flow</h3>
      <p>Файлы и папки можно упаковать в AES-архив, а затем безопасно распаковать обратно внутри того же локального диска.</p>
    </td>
  </tr>
</table>

## Ключевые сценарии

<p align="center">
  <img src="assets/github-flow.svg" alt="VantaVault Product Flow" width="100%">
</p>

### Что уже умеет проект

- локальный пароль на вход в приложение;
- автодетект нужного внешнего диска;
- уведомление, если целевой диск не подключен;
- автофокус на диске после появления в системе;
- отдельное окно настроек для параметров по умолчанию;
- открытие диска или текущей папки в Finder или Explorer;
- AES-архивирование и распаковка прямо из интерфейса;
- безопасный `lockout` вместо разрушительного автоудаления данных;
- desktop-режим через `pywebview`;
- сборка под `macOS` и `Windows`.

### Что выглядит сильнее обычного файлового helper

- интерфейс завязан не просто на список дисков, а на статус конкретного целевого тома;
- recovery-поток и AES-архивы встроены в тот же рабочий контекст;
- настройки по умолчанию позволяют превратить проект в предсказуемый личный vault;
- модель защиты не маскируется под “кибер-эффект”, а ведет себя осторожно и локально.

## Скачать

Главная точка скачивания для пользователей:

<p>
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest"><strong>Открыть Latest Release</strong></a>
</p>

В каждом релизе пользователю будут доступны:

- `VantaVault-vX.Y.Z-macos.dmg`
- `VantaVault-vX.Y.Z-windows-x64.exe`
- `SHA256`-файлы для проверки скачанного билда

Так релизы выглядят чище:

- человек сразу видит номер версии;
- `macOS` и `Windows` лежат рядом в одном релизе;
- имя файла уже объясняет, что именно скачивается.

## Для открытого репозитория

`VantaVault` теперь оформлен не только как приложение, но и как публичный GitHub-репозиторий, которым удобно пользоваться и в который удобно контрибьютить.

- есть `MIT`-лицензия для свободного использования;
- есть versioned releases с готовыми `dmg` и `exe`;
- есть шаблоны для багов, feature request и `pull request`;
- есть отдельные документы для вклада в проект, безопасности и правил сообщества;
- GitHub-витрина оформлена как продуктовая landing-страница, а не как сырой список файлов.

## Как помочь

Если хочешь внести вклад:

1. открой `issue`, если изменение крупное или спорное;
2. форкни репозиторий и сделай отдельную ветку;
3. внеси изменение и прогони локальные проверки;
4. открой `pull request` с понятным описанием и, если нужно, со скриншотами.

Быстрые ссылки:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [.github/ISSUE_TEMPLATE/bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml)
- [.github/ISSUE_TEMPLATE/feature_request.yml](.github/ISSUE_TEMPLATE/feature_request.yml)
- [.github/pull_request_template.md](.github/pull_request_template.md)

## Локальный запуск

```bash
cd "/Users/mitaro/Equilibrium/Zed/VantaVault"
python3 desktop.py
```

Для web-режима без desktop shell:

```text
http://127.0.0.1:8421
```

Или через launcher:

```bash
./main
```

## Зависимости

Runtime:

```bash
python3 -m pip install -r requirements-desktop.txt
```

Важное замечание:

- для AES-архивов нужен `pyzipper`;
- desktop-окно использует `pywebview`.

## Сборка релизов

### macOS

```bash
cd "/Users/mitaro/Equilibrium/Zed/VantaVault"
./scripts/build_mac.sh
```

Результат:

```text
release/VantaVault-mac.dmg
```

### Windows

- локально на Windows: `scripts/build_windows.ps1`
- через GitHub Actions: workflow `VantaVault Release`

### GitHub Releases

В репозитории настроен workflow: [release.yml](.github/workflows/release.yml)

Он работает так:

- создаешь тег вида `v0.2.0`;
- пушишь тег в GitHub;
- GitHub Actions собирает `dmg` и `exe`;
- assets автоматически прикрепляются к `GitHub Release`;
- страница `Releases` становится главной витриной скачивания.

Пример выпуска новой версии:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Структура проекта

| Путь | Назначение |
| --- | --- |
| `app.py` | локальный HTTP backend, логика дисков, настройки, lockout, AES-архивы |
| `desktop.py` | desktop launcher на `pywebview` |
| `web/` | интерфейс приложения |
| `assets/` | визуальные assets, включая GitHub-баннер |
| `scripts/` | сборка, очистка и генерация иконок |
| `tests/` | локальные unit-тесты |

## Документы сообщества

| Файл | Назначение |
| --- | --- |
| `CONTRIBUTING.md` | правила для участников и checklist для изменений |
| `SECURITY.md` | как сообщать о проблемах безопасности |
| `CODE_OF_CONDUCT.md` | базовые правила общения в проекте |
| `.github/ISSUE_TEMPLATE/` | шаблоны багов и feature request |
| `.github/pull_request_template.md` | структура для входящих `PR` |

## Безопасность

- пароль хранится локально в виде `PBKDF2-SHA256` хеша;
- доступ к интерфейсу идет через локальную cookie-сессию;
- после серии неверных паролей включается временный `lockout`;
- автоматическое стирание данных не используется;
- AES-архивы шифруются локально и не требуют внешнего сервиса;
- приложение ничего не отправляет в интернет.

Открытые security-issues не должны содержать exploit-детали. Для этого есть отдельный документ: [SECURITY.md](SECURITY.md).

## Проверка

Быстрый локальный прогон:

```bash
python3 -m py_compile app.py desktop.py tests/test_app.py
python3 -m unittest discover -s tests -v
```

## Статус

Проект уже выглядит как рабочий desktop-vault, а не как сырой прототип: есть локальная защита,
автодетект внешнего диска, recovery-поток и витринное оформление для GitHub-страницы репозитория.

## Лицензия

Проект распространяется по лицензии `MIT`. Подробности: [LICENSE](LICENSE).
