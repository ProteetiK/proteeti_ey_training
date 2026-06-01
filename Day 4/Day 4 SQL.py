import pandas as pd
import sqlite3

conn1 = sqlite3.connect('ey_day4.db')
cursor = conn1.cursor()
query1 = '''
CREATE TABLE IF NOT EXISTS  customers ( 
  customer_id   INTEGER PRIMARY KEY AUTOINCREMENT, 
  first_name    VARCHAR(100) NOT NULL, 
  last_name     VARCHAR(100) NOT NULL, 
  email         VARCHAR(255) UNIQUE NOT NULL, 
  phone         VARCHAR(20), 
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
); 

CREATE TABLE IF NOT EXISTS  categories ( 
  category_id   INTEGER PRIMARY KEY AUTOINCREMENT, 
  category_name VARCHAR(100) NOT NULL, 
  description   TEXT 
); 

CREATE TABLE IF NOT EXISTS  vendors ( 
  vendor_id     INTEGER PRIMARY KEY AUTOINCREMENT, 
  vendor_name   VARCHAR(150) NOT NULL, 
  contact_email VARCHAR(255) 
); 

CREATE TABLE IF NOT EXISTS products ( 
  product_id    INTEGER PRIMARY KEY AUTOINCREMENT, 
  product_name  VARCHAR(200) NOT NULL, 
  category_id   INT REFERENCES categories(category_id), 
  vendor_id     INT REFERENCES vendors(vendor_id), 
  unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0), 
  stock_qty     INT DEFAULT 0 
); 

CREATE TABLE IF NOT EXISTS orders ( 
order_id      INTEGER PRIMARY KEY AUTOINCREMENT, 
customer_id   INT NOT NULL REFERENCES customers(customer_id), 
order_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
status        
VARCHAR(20) CHECK (status IN ('Pending','Confirmed','Shipped','Delivered','Cancelled')) 
DEFAULT 'Pending' 
); 

-- Order Lines 
CREATE TABLE IF NOT EXISTS order_lines ( 
line_id       INTEGER PRIMARY KEY AUTOINCREMENT, 
order_id      
INT NOT NULL REFERENCES orders(order_id), 
product_id    INT NOT NULL REFERENCES products(product_id), 
quantity      
INT NOT NULL CHECK (quantity > 0), 
unit_price    NUMERIC(10,2) NOT NULL 
); 

-- Payments 
CREATE TABLE IF NOT EXISTS payments ( 
payment_id    INTEGER PRIMARY KEY AUTOINCREMENT, 
order_id      
INT UNIQUE NOT NULL REFERENCES orders(order_id), 
payment_date  TIMESTAMP, 
method        
VARCHAR(50) CHECK (method IN ('Card','PayPal','Bank Transfer','Wallet')), 
amount        
status        
);
'''
#pd.read_sql_query(query1, conn1)
cursor.executescript(query1)

query2 = """SELECT 
        CONCAT(C.first_name, ' ', C.last_name) AS customer_name,
        COUNT(DISTINCT O.order_id) AS total_orders,
        SUM(OL.quantity * OL.unit_price) AS total_spent,
        RANK() OVER (ORDER BY SUM(OL.quantity * OL.unit_price) DESC) AS customer_rank
        FROM customers C
        JOIN orders O ON C.customer_id = O.customer_id
        JOIN order_lines OL ON O.order_id = OL.order_id
        GROUP BY C.first_name, C.last_name;
        """
pd.read_sql_query(query2, conn1)