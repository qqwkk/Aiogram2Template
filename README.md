# 🤖 Telegram Bot Template (Aiogram 2 + PostgreSQL + Redis)

A clean and well-structured template for building scalable **Telegram bots** using **[Aiogram 2](https://docs.aiogram.dev/en/latest/)**, **PostgreSQL**, and **Redis**.  
This project is designed to help you **start faster**, **stay organized**, and **follow best practices** from day one.

---

## ✨ Features
- ⚡ **Fast & Async** — Built on **Aiogram 2** for efficient performance.
- 🗄 **PostgreSQL Support** — Reliable database integration with **asyncpg**.
- 🔄 **Redis Integration** — Perfect for caching, sessions, and rate limiting.
- 🧩 **Modular Structure** — Clear separation of handlers, services, and utilities.
- 🔐 **Environment-Based Config** — Easy `.env` setup for secrets and tokens.
- 🛠 **Scalable Design** — Ready to grow with your project.

---

## 📂 Project Structure
```
template/
├── .gitignore                 # Git ignore rules
├── env                       # Environment variables template (rename to .env)
├── LICENSE                   # License file
├── main.py                   # Entry point for the bot
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
│
├── .vscode/                  # VSCode configuration
│   └── launch.json           # Debug & run settings
│
└── bot/                      # Main bot logic
    ├── __init__.py
    ├── untils.py             # Utilities (helpers, formatters, etc.)
    │
    ├── configs/              # Configuration files
    │   ├── bot.py            # Telegram bot settings
    │   ├── databases.py      # Database config
    │   ├── db_pool.py        # PostgreSQL connection pool
    │   ├── fsm.py            # FSM states config
    │   └── __init__.py
    │
    ├── databases/            # Database access layer
    │   ├── init.py           # DB initialization script
    │   ├── postgres.py       # PostgreSQL integration
    │   ├── redis.py          # Redis integration
    │   └── __init__.py
    │
    ├── decorators/           # Custom decorators
    │   ├── admin.py          # Admin permissions check
    │   └── __init__.py
    │
    ├── functions/            # Business logic
    │   ├── admin.py          # Admin-related functions
    │   ├── dev.py            # Developer tools
    │   ├── user.py           # User-related functions
    │   └── __init__.py
    │
    ├── handlers/             # Aiogram handlers
    │   ├── admin.py          # Admin commands & callbacks
    │   ├── all.py            # Shared handlers for all users
    │   ├── dev.py            # Developer-specific commands
    │   ├── user.py           # User commands & callbacks
    │   └── __init__.py
    │
    └── keyboards/            # Inline & reply keyboards
        ├── admin.py          # Admin keyboards
        ├── user.py           # User keyboards
        └── __init__.py
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
https://github.com/new?template_name=Aiogram2Template&template_owner=qqwkk
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
1. Duplicate the **`env`** file and rename it to **`.env`**:
   ```bash
   cp env .env
   ```
2. Open `.env` and add your:
   - Telegram Bot Token
   - PostgreSQL credentials
   - Redis credentials

---

## 🛠 Example `.env`
```ini
# Telegram API @BotFather
BOT_TOKEN=YOUR_BOT_TOKEN

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bot_db
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=bot_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

---

### 4. Run the bot
```bash
python main.py
```


---

## 📦 Tech Stack
| Component      | Technology      | Description                              |
|--------------|-----------------|---------------------------------------|
| **Language** | Python 3.11+    | Modern, fast, and async-ready        |
| **Framework**| Aiogram 2.25.2  | Lightweight, fully asynchronous bot framework |
| **Database** | PostgreSQL      | Reliable relational DB              |
| **Cache**    | Redis          | Session storage & caching           |
| **Config**   | python-dotenv  | Environment variable management    |

---

## 🛡 Recommendations
- Keep **secrets** in `.env`
- Organize handlers inside `app/handlers`
- Use Redis for **sessions & caching**
- Write async DB queries for better performance

---


### 🌟 Star this repository if you find it useful!