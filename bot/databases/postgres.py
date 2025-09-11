from typing import Optional, Tuple
from bot.configs import db_pool
from datetime import datetime, timedelta
from aiogram.types import Message, CallbackQuery
import asyncpg
from typing import Dict, Any


class User:
    @staticmethod
    async def select(user_id):
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            return dict(row) if row else None
        finally:
            await db_pool.pool.release(conn)

    @staticmethod
    async def select_id(user_id):
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            row = await conn.fetchrow("SELECT id FROM users WHERE user_id = $1", user_id)
            return row["id"] if row else None
        finally:
            await db_pool.pool.release(conn)

    @staticmethod
    async def select_by_id(id):
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", id)
            return dict(row) if row else None
        finally:
            await db_pool.pool.release(conn)

    @staticmethod
    async def insert(user_id, username, first_name, last_name, language_code, is_premium):
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, language_code, is_premium)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, username, first_name, last_name, language_code, is_premium)
        finally:
            await db_pool.pool.release(conn)

class Admin:
    @staticmethod
    async def select_id(users_id: int) -> Optional[int]:
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            row = await conn.fetchrow("SELECT id FROM admins WHERE users_id = $1", users_id)
            return row["id"] if row else None
        finally:
            await db_pool.pool.release(conn)

    @staticmethod
    async def select(user_id: int) -> Optional[Dict[str, Any]]:
        conn: asyncpg.Connection = await db_pool.pool.acquire()
        try:
            row = await conn.fetchrow("SELECT * FROM admins WHERE users_id = $1", user_id)
            return dict(row) if row else None
        finally:
            await db_pool.pool.release(conn)