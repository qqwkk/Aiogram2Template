import asyncpg

pool: asyncpg.Pool = None

async def create_pool(user, password, database, host, port):
    global pool
    pool = await asyncpg.create_pool(
        user=user,
        password=password,
        database=database,
        host=host,
        port=int(port)
    )