import pandas as pd
import sqlite3

conn1 = sqlite3.connect('ey_day4.db')
cursor = conn1.cursor()
query1 = '''CREATE SCHEMA shopey; 

CREATE TABLE shopey.customers ( 
  customer_id   SERIAL PRIMARY KEY, 
  first_name    VARCHAR(100) NOT NULL, 
  last_name     VARCHAR(100) NOT NULL, 
  email         VARCHAR(255) UNIQUE NOT NULL, 
  phone         VARCHAR(20), 
  created_at    TIMESTAMP DEFAULT NOW() 
); 

CREATE TABLE shopey.categories ( 
  category_id   SERIAL PRIMARY KEY, 
  category_name VARCHAR(100) NOT NULL, 
  description   TEXT 
); 

CREATE TABLE shopey.vendors ( 
  vendor_id     SERIAL PRIMARY KEY, 
  vendor_name   VARCHAR(150) NOT NULL, 
  contact_email VARCHAR(255) 
); 

CREATE TABLE shopey.products ( 
  product_id    SERIAL PRIMARY KEY, 
  product_name  VARCHAR(200) NOT NULL, 
  category_id   INT REFERENCES shopey.categories(category_id), 
  vendor_id     INT REFERENCES shopey.vendors(vendor_id), 
  unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0), 
  stock_qty     INT DEFAULT 0 
); 

CREATE TABLE shopey.orders ( 
order_id      
SERIAL PRIMARY KEY, 
customer_id   INT NOT NULL REFERENCES shopey.customers(customer_id), 
order_date    TIMESTAMP DEFAULT NOW(), 
status        
VARCHAR(20) CHECK (status IN ('Pending','Confirmed','Shipped','Delivered','Cancelled')) 
DEFAULT 'Pending' 
); 

-- Order Lines 
CREATE TABLE shopey.order_lines ( 
line_id       
SERIAL PRIMARY KEY, 
order_id      
INT NOT NULL REFERENCES shopey.orders(order_id), 
product_id    INT NOT NULL REFERENCES shopey.products(product_id), 
quantity      
INT NOT NULL CHECK (quantity > 0), 
unit_price    NUMERIC(10,2) NOT NULL 
); 

-- Payments 
CREATE TABLE shopey.payments ( 
payment_id    SERIAL PRIMARY KEY, 
order_id      
INT UNIQUE NOT NULL REFERENCES shopey.orders(order_id), 
payment_date  TIMESTAMP, 
method        
VARCHAR(50) CHECK (method IN ('Card','PayPal','Bank Transfer','Wallet')), 
amount        
status        
);

NUMERIC(10,2) NOT NULL, 
VARCHAR(20) CHECK (status IN ('Pending','Paid','Failed','Refunded')) DEFAULT 'Pending'
'''
#pd.read_sql_query(query1, conn1)
cursor.executescript(query1)

query2 = """SELECT first_name+last_name as distict count(order_id) as total_orders, (sum(OL.quantity*OL.unit_price)) as total_spent, RANK() over (order by total_spent desc) as customer_rank
        from shopey.customers C 
        join shopey.orders O on C.customerId = o.customerId
        join shopey.order_lines OL on o.orderId = OL.orderId
        """
pd.read_sql_query(query2, conn1)