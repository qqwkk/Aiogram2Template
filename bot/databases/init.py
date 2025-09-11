from datetime import datetime
import asyncpg
from bot.configs import db_pool

class UserTable:
    @staticmethod
    async def create():
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT,
            language_code TEXT,
            language TEXT,
            is_premium BOOLEAN DEFAULT FALSE,
            joined_at TIMESTAMP NOT NULL DEFAULT now(),
            last_active TIMESTAMP NOT NULL DEFAULT now()
        );
        """
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            await conn.execute(query)
        finally:
            await db_pool.pool.release(conn)

class AdminTable:
    @staticmethod
    async def create():
        query = """
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            users_id INTEGER NOT NULL,
            added_by INTEGER DEFAULT 0,
            added_at TIMESTAMP DEFAULT now()
        );
        """
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            await conn.execute(query)
        finally:
            await db_pool.pool.release(conn)

async def init_db():
    await UserTable.create()
    await AdminTable.create()