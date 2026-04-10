import aiosqlite
from config import DB_PATH
from datetime import datetime
from typing import Optional, Dict, List

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price_stars INTEGER NOT NULL,
                supercell_id TEXT,
                status TEXT DEFAULT 'pending',
                telegram_charge TEXT,
                provider_charge TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        """)
        await db.commit()

async def create_order(user_id: int, username: str, product_id: str, product_name: str, price_stars: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, username, product_id, product_name, price_stars, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, product_id, product_name, price_stars, datetime.utcnow().isoformat())
        )
        await db.commit()
        return cursor.lastrowid

async def update_order_supercell_id(order_id: int, supercell_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET supercell_id = ?, status = 'awaiting_payment' WHERE id = ?", (supercell_id, order_id))
        await db.commit()

async def mark_order_paid(order_id: int, telegram_charge: str, provider_charge: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'paid', telegram_charge = ?, provider_charge = ? WHERE id = ?", 
                        (telegram_charge, provider_charge, order_id))
        await db.commit()

async def mark_order_completed(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'completed', completed_at = ? WHERE id = ?", 
                        (datetime.utcnow().isoformat(), order_id))
        await db.commit()

async def get_order(order_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_user_orders(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
