import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Product:
    id: str
    name: str
    emoji: str
    description: str
    price_stars: int

PRODUCTS = {
    "brawl_pass": Product("brawl_pass", "Brawl Pass", "🎫", "Стандартный Brawl Pass", 250),
    "brawl_pass_plus": Product("brawl_pass_plus", "Brawl Pass+", "🎫✨", "Brawl Pass с доп. наградами", 400),
    "pro_pass": Product("pro_pass", "Pro Pass", "🏆", "Максимальный Pro Pass", 600),
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DB_PATH = "shop.db"
