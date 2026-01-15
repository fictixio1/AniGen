"""Database connection pool and transaction helpers."""

import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager
from config import config

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL connection pool manager."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool."""
        if self.pool is None:
            logger.info(f"Connecting to database: {config.database_url}")
            self.pool = await asyncpg.create_pool(
                config.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
            self.pool = None

    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            async with db.transaction() as conn:
                await conn.execute("INSERT INTO ...")
        """
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Execute a query and return all results."""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Execute a query and return a single row."""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Execute a query and return a single value."""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database instance
db = Database()
