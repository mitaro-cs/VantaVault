# Getting Started

`VantaVault` можно запустить двумя способами:

1. скачать готовый релиз из `GitHub Releases`;
2. развернуть приложение локально из репозитория одной командой.

## Вариант 1. Скачать готовый релиз

Открой:

- `https://github.com/mitaro-cs/VantaVault/releases/latest`

Скачай файл под свою систему:

- `VantaVault-vX.Y.Z-macos.dmg`
- `VantaVault-vX.Y.Z-windows-x64.exe`

Если хочешь проверить загрузку, рядом лежат `SHA256`-файлы.

## Вариант 2. Запуск из репозитория

### macOS / Linux

```bash
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
chmod +x main
./main
```

### Windows

```powershell
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
.\main.ps1
```

Или двойным кликом:

- `main.bat`

## Что делает bootstrap

При первом запуске скрипт:

- создает локальное окружение `.venv`;
- ставит зависимости из `requirements-desktop.txt`;
- запускает `desktop.py`.

При следующих запусках:

- использует уже готовое окружение;
- переустанавливает зависимости только если изменился `requirements-desktop.txt`.

## Если нужен только install

### macOS / Linux

```bash
./main --install-only
```

### Windows

```powershell
.\main.ps1 --install-only
```

## Первый запуск

После старта приложение:

- откроет локальное окно desktop-app;
- предложит создать пароль, если vault запускается впервые;
- покажет статус целевого внешнего диска;
- даст открыть настройки и выбрать диск по умолчанию.

Если desktop shell недоступен, `VantaVault` откроет локальную web-версию в браузере.
