<p align="center">
  <img src="assets/github-banner.svg" alt="VantaVault GitHub Banner" width="60%" style="border-radius:32px;box-shadow:0 8px 32px #0002;">
</p>

<h1 align="center">VantaVault</h1>

<p align="center">
  <strong>🔒 Твой личный сейф для внешних дисков — просто, красиво, безопасно!</strong><br>
  <em>Доступно для всех. Без облака. Только ты и твои файлы.</em>
</p>

<p align="center">
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Latest Release" src="https://img.shields.io/github/v/release/mitaro-cs/VantaVault?display_name=tag&style=for-the-badge&label=latest%20release&color=F5F5F7&labelColor=111111">
  </a>
  <a href="https://github.com/mitaro-cs/VantaVault/releases/latest">
    <img alt="Download" src="https://img.shields.io/badge/Download-Releases-F5F5F7?style=for-the-badge&labelColor=111111">
  </a>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-F5F5F7?style=for-the-badge&labelColor=111111">
  <img alt="macOS / Windows" src="https://img.shields.io/badge/macOS%20%2F%20Windows-supported-F5F5F7?style=for-the-badge&labelColor=111111">
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#download">Download</a> ·
  <a href="#run-from-source">Run From Source</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#security">Security</a>
</p>

## 🚀 Для кого VantaVault?

- Для всех, кто ценит приватность и простоту
- Для студентов, фрилансеров, семей и профессионалов
- Для тех, кто хочет хранить файлы на своих условиях

---

## 🌟 Ключевые возможности

<div align="center">
  <img src="assets/premium-icons.svg" alt="Premium Features" width="420px" style="margin-bottom:24px;">
</div>

- **Локальная безопасность** — только у вас, без облака
- **Диск-ориентированность** — автоматическое определение и защита
- **Архивирование** — шифрование и восстановление в пару кликов


## 📥 Как начать?

1. <b>Скачай последнюю версию:</b> [Релизы](https://github.com/mitaro-cs/VantaVault/releases/latest)
2. <b>Установи и запусти:</b>
   - macOS: <code>VantaVault-mac.dmg</code>
   - Windows: <code>VantaVault-windows-x64.exe</code>
3. <b>Следуй простым подсказкам на экране!</b>

## 🛠️ Запуск из исходников

<details>
<summary>macOS / Linux</summary>

```bash
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
chmod +x main
./main
```
</details>

<details>
<summary>Windows</summary>

```powershell
git clone https://github.com/mitaro-cs/VantaVault.git
cd VantaVault
.\main.ps1
```
или открой <code>main.bat</code>
</details>

## Product Flow

<p align="center">
  <img src="assets/github-flow.svg" alt="VantaVault Product Flow" width="60%" style="margin:32px 0;">
</p>

---

<p align="center">
  <img src="assets/mockup-premium.png" alt="VantaVault Premium Mockup" width="50%" style="border-radius:32px;box-shadow:0 8px 32px #0003;">
  <br><sub>Премиальный интерфейс. Ваши данные — ваша приватность.</sub>
</p>


## 📚 Документация и поддержка

- [Начало работы](docs/GETTING_STARTED.md)
- [FAQ](docs/FAQ.md)
- [Техническая поддержка](SUPPORT.md)
- [Внести вклад](CONTRIBUTING.md)

## 🛡️ Безопасность

- Локальное хранение паролей (PBKDF2-SHA256)
- Защита сессии и временная блокировка при ошибках
- Локальное шифрование архивов (AES)

Подробнее: [SECURITY.md](SECURITY.md)

## 📝 Лицензия

MIT. Свободно для всех. [LICENSE](LICENSE)

---

<p align="center">
  <sub>Сделано с ❤️ для людей. Присоединяйся!</sub>
</p>
