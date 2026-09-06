# Inventory Management System

A web-based Inventory Management System built using **Python Flask, MySQL, HTML, CSS, and JavaScript**.

## Features

- Product Management
- Supplier Management
- Warehouse Management
- Purchase Management
- Sales Management
- Stock Tracking
- Low Stock Monitoring
- Inventory Reports

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript

## Project Structure

```text
Inventory-Management-System/
│
├── app.py
├── config.py
├── init_db.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── routes/
│   ├── product_routes.py
│   ├── purchase_routes.py
│   ├── report_routes.py
│   ├── sales_routes.py
│   ├── stock_routes.py
│   ├── supplier_routes.py
│   └── warehouse_routes.py
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/


Installation & Setup
1. Clone the Repository
git clone https://github.com/anshitamaturkar12/Inventory-Management-System.git

Go to the project folder:

cd Inventory-Management-System
2. Install Python Dependencies

Make sure Python is installed, then run:

pip install -r requirements.txt
3. Install and Start MySQL

Make sure MySQL Server is installed and running.

Login to MySQL:

mysql -u root -p
4. Create the Database

Inside MySQL, create the database:

CREATE DATABASE inventory_db;

Then exit MySQL:

exit;
5. Create the .env File

Create a file named:

.env

in the project root folder.

Add your local MySQL details:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=inventory_db

Do not upload .env to GitHub.

6. Initialize the Database

Run:

python init_db.py

This will create the required database tables.

7. Run the Application

Start the Flask application:

python app.py

You should see something similar to:

Running on http://127.0.0.1:5000
8. Open the Website

Open your browser and go to:

http://127.0.0.1:5000

The Inventory Management System will now be running locally.

Important Notes
MySQL must be running before starting the Flask application.
Each team member should create their own .env file.
Never upload passwords or other sensitive information to GitHub.
Install all dependencies using requirements.txt.
## 🗄️ Database Architecture & Relationships

### Database Name: *inventory_db*

### Tables Overview:
1. *products*: product_id (PK), product_name, category, price, minimum_stock.
2. *suppliers*: supplier_id (PK), supplier_name, phone, email, address.
3. *warehouses*: warehouse_id (PK), warehouse_name, location.
4. *stock*: stock_id (PK), product_id (FK), warehouse_id (FK), quantity, UNIQUE(product_id, warehouse_id).
5. *purchase_orders*: purchase_id (PK), supplier_id (FK), warehouse_id (FK), order_date, total_amount.
6. *purchase_items*: purchase_item_id (PK), purchase_id (FK), product_id (FK), quantity, price.
7. *sales*: sale_id (PK), product_id (FK), warehouse_id (FK), customer_name, quantity, sale_price, sale_date.

### Entity Relationships:
text
           [SUPPLIERS]
                | (1)
                |
                | (M)
      [PURCHASE_ORDERS] ──────────┐
                | (1)             |
                |                 |
                | (M)             |
       [PURCHASE_ITEMS]           |
                | (M)             |
                |                 |
                | (1)             | (M)
           [PRODUCTS]        [WAREHOUSES]
             |      \           /     |
         (1) |       \ (1) (1) /      | (1)
             |        \       /       |
         (M) |         [STOCK]        | (M)
          [SALES] ────────────────────┘


---
