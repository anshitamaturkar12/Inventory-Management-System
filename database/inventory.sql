-- ==========================================================
-- Simple Inventory Management System Database
-- Database: inventory_db
-- Target: MySQL Server / MySQL Workbench
-- ==========================================================

-- 1. Create the Database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS inventory_db;
USE inventory_db;

-- 2. Drop existing tables if re-running (child tables first to avoid FK errors)
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS purchase_items;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS products;

-- ==========================================================
-- Table: products
-- Stores details about products offered or stored
-- ==========================================================
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    minimum_stock INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: suppliers
-- Stores suppliers from whom products are purchased
-- ==========================================================
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: warehouses
-- Stores warehouse storage facilities
-- ==========================================================
CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: stock
-- Tracks current stock quantity for each product in each warehouse
-- ==========================================================
CREATE TABLE stock (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_warehouse UNIQUE (product_id, warehouse_id),
    CONSTRAINT fk_stock_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_stock_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: purchase_orders
-- Records purchase order headers from suppliers
-- ==========================================================
CREATE TABLE purchase_orders (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_purchase_supplier FOREIGN KEY (supplier_id) 
        REFERENCES suppliers(supplier_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_purchase_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: purchase_items
-- Records line items for each purchase order
-- ==========================================================
CREATE TABLE purchase_items (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_item_purchase FOREIGN KEY (purchase_id) 
        REFERENCES purchase_orders(purchase_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Table: sales
-- Records customer sales transactions
-- ==========================================================
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    sale_price DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_sales_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- Sample Realistic Seed Data
-- ==========================================================

-- 1. Insert Products
INSERT INTO products (product_id, product_name, category, price, minimum_stock) VALUES
(1, 'Laptop', 'Electronics', 55000.00, 5),
(2, 'Keyboard', 'Accessories', 800.00, 10),
(3, 'Mouse', 'Accessories', 450.00, 15),
(4, 'Monitor', 'Electronics', 12000.00, 6),
(5, 'Printer', 'Office Equipment', 15000.00, 4);

-- 2. Insert Suppliers
INSERT INTO suppliers (supplier_id, supplier_name, phone, email, address) VALUES
(1, 'ABC Electronics', '9876543210', 'info@abcelectronics.com', '123 Tech Park, Bangalore'),
(2, 'XYZ Traders', '9876543211', 'contact@xyztraders.com', '45 Market Road, Mumbai'),
(3, 'Tech World', '9876543212', 'sales@techworld.com', '78 Industrial Area, Delhi');

-- 3. Insert Warehouses
INSERT INTO warehouses (warehouse_id, warehouse_name, location) VALUES
(1, 'Main Warehouse', 'Sector 18, Gurugram'),
(2, 'Secondary Warehouse', 'Electronic City, Bangalore');

-- 4. Insert Initial Stock
-- Notice: Keyboard (qty 3 <= min 10) and Monitor (qty 2 <= min 6) are LOW STOCK!
INSERT INTO stock (product_id, warehouse_id, quantity) VALUES
(1, 1, 15),  -- Laptop in Main Warehouse (In Stock)
(2, 1, 3),   -- Keyboard in Main Warehouse (LOW STOCK: 3 <= 10)
(3, 1, 25),  -- Mouse in Main Warehouse (In Stock)
(4, 2, 2),   -- Monitor in Secondary Warehouse (LOW STOCK: 2 <= 6)
(5, 2, 8);   -- Printer in Secondary Warehouse (In Stock)

-- 5. Insert Sample Purchases
INSERT INTO purchase_orders (purchase_id, supplier_id, warehouse_id, order_date, total_amount) VALUES
(1, 1, 1, '2026-08-20', 550000.00),
(2, 2, 1, '2026-08-22', 16000.00),
(3, 3, 2, '2026-08-25', 60000.00);

INSERT INTO purchase_items (purchase_item_id, purchase_id, product_id, quantity, price) VALUES
(1, 1, 1, 10, 55000.00),
(2, 2, 2, 20, 800.00),
(3, 3, 5, 4, 15000.00);

-- 6. Insert Sample Sales
INSERT INTO sales (sale_id, product_id, warehouse_id, customer_name, quantity, sale_price, sale_date) VALUES
(1, 1, 1, 'Rohan Sharma', 2, 58000.00, '2026-08-28'),
(2, 3, 1, 'Priya Patel', 5, 500.00, '2026-08-29'),
(3, 5, 2, 'Apex Solutions', 1, 16500.00, '2026-08-30');
