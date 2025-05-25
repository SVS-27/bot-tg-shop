import sqlite3

# Подключаемся к базе данных (если файла нет, он создастся автоматически)
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# Таблица товаров
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
""")

# Таблица корзины
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id)
)
""")

# Таблица заказов
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_price INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
)
""")

conn.commit()
conn.close()


def add_product(name, price):
    """Добавляет товар в базу данных"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()


def get_products():
    """Получает список всех товаров"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products


def add_to_cart(user_id, product_id, quantity=1):
    """Добавляет товар в корзину пользователя с указанием количества"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        new_quantity = result[0] + quantity
        cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?", (new_quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, product_id, quantity))

    conn.commit()
    conn.close()


def remove_from_cart(user_id, product_id):
    """Удаляет 1 шт. товара из корзины, если количество > 1, иначе удаляет полностью"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        if result[0] > 1:
            new_quantity = result[0] - 1
            cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?", (new_quantity, user_id, product_id))
        else:
            cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))

    conn.commit()
    conn.close()


def get_cart(user_id):
    """Возвращает список товаров в корзине пользователя"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, cart.quantity, products.price, products.id 
        FROM cart 
        JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id=?
    """, (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items


def create_order(user_id):
    """Создает заказ из корзины пользователя"""
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.id, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=?
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        conn.close()
        return None

    total_price = sum(item[1] * item[2] for item in cart_items)

    cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (?, ?)", (user_id, total_price))
    order_id = cursor.lastrowid

    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))

    conn.commit()
    conn.close()
    return order_id