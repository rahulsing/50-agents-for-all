"""Creates a small sample shop database (SQLite) used by the SQL agents (15, 42)."""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


def create_shop_db(path: Path) -> Path:
    if path.exists():
        return path
    rng = random.Random(42)  # fixed seed: everyone gets the same data
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT, joined DATE);
        CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                             product_id INTEGER REFERENCES products(id), quantity INTEGER, order_date DATE);
    """)
    cities = ["London", "Paris", "Berlin", "Madrid", "Rome"]
    names = ["Alice", "Bob", "Chen", "Diana", "Emre", "Fatima", "George", "Hana", "Ivan", "Julia",
             "Kofi", "Lena", "Mateo", "Nora", "Omar"]
    for i, n in enumerate(names, 1):
        cur.execute("INSERT INTO customers VALUES (?,?,?,?)",
                    (i, n, cities[i % 5], date(2025, 1, 1) + timedelta(days=rng.randint(0, 500))))
    products = [("Laptop", "Electronics", 999), ("Headphones", "Electronics", 149), ("Monitor", "Electronics", 249),
                ("Desk", "Furniture", 320), ("Chair", "Furniture", 180), ("Lamp", "Furniture", 45),
                ("Notebook", "Stationery", 4.5), ("Pen pack", "Stationery", 7), ("Backpack", "Accessories", 65),
                ("Water bottle", "Accessories", 18)]
    for i, (n, c, p) in enumerate(products, 1):
        cur.execute("INSERT INTO products VALUES (?,?,?,?)", (i, n, c, p))
    for i in range(1, 201):
        cur.execute("INSERT INTO orders VALUES (?,?,?,?,?)",
                    (i, rng.randint(1, 15), rng.randint(1, 10), rng.randint(1, 4),
                     date(2026, 1, 1) + timedelta(days=rng.randint(0, 270))))
    con.commit()
    con.close()
    return path
