<div align="center">

# 🏷️ StickerPack-Migrator

> **All-in-one, high-performance Telegram sticker pack cloner and renamer bot built with Python and aiogram v3.**

Sticker-Renamer allows users to seamlessly clone, rename, and customize existing static, animated, or video sticker packs under a brand-new custom link and display name instantly.

<br>

 <a href="https://t.me/MrBossRoBot">
    <img src="https://img.shields.io/badge/_𝗧𝗥𝗬_𝗟𝗜𝗩𝗘_𝗕𝗢𝗧-24A1EF?style=for-the-badge&logo=telegram&logoColor=white" alt="Try Live Bot">
</a>

</div>

---

## ✨ Features

### 📦 Multi-Format Pack Cloning
- **🎨 Static, Animated & Video Support**: Automatically detects and preserves the exact format type (`.png`/`.webp`, `.tgs`, or `.webm`) of the source sticker pack.
- **⚡ Smart File ID Reuse**: Bypasses heavy disk downloading by mapping existing Telegram `file_id` strings directly into the new pack for instant generation.
- **🖼️ Custom Icons & Thumbnails**: Upload a custom icon for your cloned pack or use `/skip` to automatically default to the first sticker from the source pack.
- **🔗 Bot Namespace Integration**: Automatically appends the required bot username suffix (`_by_<bot_username>`) to ensure successful creation via Telegram's API.

### ⚙️ User Experience & Wizard
- **🧙‍♂️ Step-by-Step FSM Wizard**: Smooth conversation flow guiding users through link detection, title configuration, shortname validation, and icon selection.
- **🛡️ Shortname Validation**: Built-in regex filters ensuring custom short links only contain valid characters (letters, numbers, and underscores).
- **🚀 Live Error Handling**: Gracefully catches Telegram API limits (`FloodWait`), bad requests, or invalid links with descriptive alerts.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Bot Framework**: [aiogram v3](https://docs.aiogram.dev/)
- **Environment Management**: `python-dotenv`
- **License**: MIT

---

## 🚀 Quick Start

### Prerequisites

- [Python](https://www.python.org/) (v3.10+ recommended)
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 1. Clone & Install Dependencies

```bash
git clone [https://github.com/MrBoss002/StickerPack-Migrator.git](https://github.com/MrBoss002/StickerPack-Migrator.git)
cd StickerPack-Migrator
```
```
pip install -r requirements.txt
```

### 2. Environment Setup

Copy .env.example to .env in the root directory and configure your token:

```code snippet
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
```

### 3. Run the Bot

```bush
python -m src.main
```

---

## ⚙️ Environment Variables

To run **Sticker-Renamer**, configure the following environment variable in your local `.env` file or deployment dashboard:

### 🔴 Required Variables
| Variable Name | Description | Example |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot API Token from [@BotFather](https://t.me/BotFather) | `123456789:ABCdefGHIjklMNO...` |

---

## 🚀 Deployment Guide

1. **Star this repository** to support the project! ⭐ &nbsp;&nbsp; <a href="https://github.com/YOUR_USERNAME/Sticker-Renamer">
    <img src="https://img.shields.io/badge/Star%20Repo-1f2328?style=for-the-badge&logo=github&logoColor=white" alt="Star Repo">
  </a>

2. **Fork this repository** to your own GitHub account. 🍴 &nbsp;&nbsp; <a href="https://github.com/YOUR_USERNAME/Sticker-Renamer/fork">
    <img src="https://img.shields.io/badge/Fork%20Repo-1f2328?style=for-the-badge&logo=git&logoColor=white" alt="Fork Repo">
  </a>

3. Deploy to your preferred Python hosting provider (e.g., Render, Railway, Koyeb) using a Background Worker configuration with the following command:
   - **Start Command:** `python -m src.main`

---

## 📄 License
> This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

---

<div align="center">

## ☕ Support & Community

If Sticker-Renamer saved you time or made managing your sticker collections easier, consider supporting the project!

| ☕ Support Developer | 🌐 Updates Channel | ⛑ Need Assistance |
| :---: | :---: | :---: |
| [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/MrBoss002) | [![Updates](https://img.shields.io/badge/Updates-Channel-FF0055?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/MrBossBotz) | [![Support](https://img.shields.io/badge/Support-Group-229ED9?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/MrBossSupport) |

<br />

**StickerPack-Migrator** • Built with ❤️ for the open-source community.

</div>
