import sqlite3

db = sqlite3.connect(
    "support.db",
    check_same_thread=False
)


def init_db():

    db.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        sku TEXT PRIMARY KEY,
        name TEXT,
        qty INTEGER,
        price REAL
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        qty INTEGER,
        total REAL,
        status TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        issue TEXT,
        status TEXT
    )
    """)

    db.commit()


def seed_inventory():

    count = db.execute(
        "SELECT COUNT(*) FROM inventory"
    ).fetchone()[0]

    if count > 0:
        return

    db.executemany(
        """
        INSERT INTO inventory
        VALUES (?,?,?,?)
        """,
        [
            (
                "KB-01",
                "Mechanical keyboard",
                12,
                129.0
            ),
            (
                "HUB-2",
                "USB-C hub",
                0,
                58.0
            ),
            (
                "MON-4",
                "4K monitor",
                5,
                410.0
            )
        ]
    )

    db.commit()


def show_state():

    print("\nOrders")

    rows = db.execute(
        """
        SELECT
            id,
            sku,
            qty,
            total,
            status
        FROM orders
        """
    ).fetchall()

    for row in rows:
        print(row)

    print("\nInventory")

    rows = db.execute(
        """
        SELECT
            sku,
            qty
        FROM inventory
        """
    ).fetchall()

    for row in rows:
        print(row)