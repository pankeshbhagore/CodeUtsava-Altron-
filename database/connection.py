import os
import asyncio
import asyncpg
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/privdb")

# Sync Connection Pool (psycopg2)
try:
    sync_pool = psycopg2.pool.SimpleConnectionPool(
        1,
        20,
        DATABASE_URL
    )
except psycopg2.DatabaseError as e:
    print(f"Error creating connection pool: {e}")
    sync_pool = None

def get_db_connection():
    if sync_pool:
        return sync_pool.getconn()
    return psycopg2.connect(DATABASE_URL)

def release_db_connection(conn):
    if sync_pool:
        sync_pool.putconn(conn)
    else:
        conn.close()

# Async Connection Pool (asyncpg)
_async_pool = None

async def get_async_pool():
    global _async_pool
    if _async_pool is None:
        _async_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=20)
    return _async_pool

async def get_async_connection():
    pool = await get_async_pool()
    return await pool.acquire()

async def release_async_connection(conn):
    pool = await get_async_pool()
    await pool.release(conn)
