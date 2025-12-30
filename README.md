# 🎤 Kanye Says — Python GUI Quote App

A feature-rich Python Tkinter desktop application that fetches iconic Kanye West quotes from a live API, with offline fallback support, favorites management, quote history, clipboard copying, auto-refresh, and social sharing — all in a modern dark-themed UI.

## ✨ Features

- 🎤 Fetch random Kanye West quotes via public API
- 🌐 Offline fallback quotes when internet/API fails
- ❤️ Save & manage favorite quotes
- 📜 Quote history with timestamps (JSON persistence)
- 📋 Copy quotes to clipboard
- 🐦 Share quotes on Twitter instantly
- 🔄 Auto-refresh quotes every 10 seconds
- 🧵 Multithreaded API calls (no UI freezing)
- ⌨️ Keyboard shortcuts for power users
- 💾 Persistent local storage using JSON files

## 🖼️ UI Overview

- Dark-themed, modern Tkinter interface
- Canvas-based quote card layout
- Favorite indicator with visual feedback
- Loading animations and status messages

## 🛠️ Tech Stack

- Python
- Tkinter (GUI)
- Requests (API handling)
- Threading (background tasks)
- JSON (local data persistence)
- pyperclip (clipboard support)

##📁 Project Structure

```bash
├── images/
│   ├── background.png
│   └── kanye.png
├── data/
│   ├── favorites.json
│   └── history.json
├── main.py
└── README.md
```

## ⚙️ Installation & Usage
### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/kanye-says.git
cd kanye-says
```
### 2️⃣ Install dependencies
```bash
pip install requests pyperclip
````
### 3️⃣ Run the app
```bash
python main.py
```

## ⌨️ Keyboard Shortcuts
| Key |	Action |
|-----|--------|
| Space / Enter |	New quote |
| F |	Favorite / Unfavorite |
| C |	Copy quote |
| Esc |	Exit app |

## 📡 API Used

- Kanye Rest API
-- Provides random Kanye West quotes
--- App automatically switches to local fallback quotes if API is unavailable.

## 🧠 What This Project Demonstrates

- Object-Oriented Programming (OOP)
- Clean, modular architecture
- GUI development with Tkinter
- API integration & robust error handling
- Multithreading for responsive UI
- Persistent local data storage
- UX-focused design decisions

## 🚀 Possible Enhancements

- Export favorites to TXT/PDF
- Theme toggle (Dark / Light mode)
- Search & filter favorites
- Package as standalone EXE

## 👨‍💻 Author

### Shaqran Hussain
Python Developer

## 🌐 Portfolio: https://shaqranhussain.dev
