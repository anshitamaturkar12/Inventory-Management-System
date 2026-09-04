# 📦 Inventory Management System (BTech College Project)

A clean, beginner-friendly, and fully functional **Inventory Management System** website built using **HTML5, CSS3, Vanilla JavaScript, Python Flask**, and **MySQL**.

This project manages products, suppliers, warehouses, stock levels, purchases, and sales, with automatic stock updates, stock validations, and real-time inventory reports.

---

## 🛠️ Technologies Used

* **Frontend**: HTML5, CSS3 (Modern Light UI, responsive layout, status badges), Vanilla JavaScript
* **Backend**: Python 3, Flask framework (Modular architecture using Flask Blueprints)
* **Database**: MySQL Server 8.0+
* **Database Management**: MySQL Workbench / Python script
* **Database Connector**: `mysql-connector-python`

---

## 📁 Project Directory Structure

```text
InventoryManagementSystem/
│
├── app.py                      # Flask main entry point, KPI dashboard & error handlers
├── config.py                   # MySQL database configuration & connection factory
├── init_db.py                  # Automatic database & seed data initialization script
├── .env                        # Active environment variables (MySQL credentials)
├── .env.example                # Template for environment variables
├── requirements.txt            # Python dependencies (Flask, mysql-connector-python, python-dotenv)
├── README.md                   # Complete documentation, setup guide & viva questions
│
├── database/
│   └── inventory.sql           # MySQL DDL schema + realistic sample seed data
│
├── routes/
│   ├── __init__.py             # Routes package marker
│   ├── product_routes.py       # CRUD & search for Products
│   ├── supplier_routes.py      # CRUD & search for Suppliers
│   ├── warehouse_routes.py     # CRUD for Warehouses
│   ├── stock_routes.py         # Stock monitoring, warehouse filtering & direct updates
│   ├── purchase_routes.py      # Purchase orders (auto-increments warehouse stock)
│   ├── sales_routes.py         # Sales orders (validates stock, auto-decrements stock)
│   └── report_routes.py        # Low stock report, Supplier-wise JOIN report, Warehouse report
│
├── templates/
│   ├── base.html               # Master layout: responsive sidebar, topbar, flash alerts
│   ├── dashboard.html          # Stats cards, low stock alerts, recent purchases & sales
│   ├── products.html           # Products list with search and action buttons
│   ├── add_product.html        # Form to add a new product
│   ├── edit_product.html       # Form to edit an existing product
│   ├── suppliers.html          # Suppliers list with search
│   ├── add_supplier.html       # Form to add a new supplier
│   ├── edit_supplier.html      # Form to edit supplier details
│   ├── warehouses.html         # Warehouses list
│   ├── add_warehouse.html      # Form to add a new storage warehouse
│   ├── edit_warehouse.html     # Form to edit warehouse details
│   ├── stock.html              # Stock overview with warehouse filter & quick update
│   ├── purchases.html          # Purchase order history
│   ├── add_purchase.html       # Form to record purchase order (auto-updates stock)
│   ├── sales.html              # Sales history
│   ├── add_sale.html           # Form to record sale (validates stock availability)
│   └── reports.html            # Low stock, Supplier-wise & Warehouse-wise reports
│
└── static/
    ├── css/
    │   └── style.css           # Clean modern light theme, badges, tables, responsive styles
    └── js/
        └── script.js           # Live date, auto-dismiss alerts, mobile sidebar toggle
```

---

## 🗄️ Database Architecture & Relationships

Database Name: **`inventory_db`**

### Tables Overview:
1. **`products`**: `product_id` (PK), `product_name`, `category`, `price`, `minimum_stock`.
2. **`suppliers`**: `supplier_id` (PK), `supplier_name`, `phone`, `email`, `address`.
3. **`warehouses`**: `warehouse_id` (PK), `warehouse_name`, `location`.
4. **`stock`**: `stock_id` (PK), `product_id` (FK), `warehouse_id` (FK), `quantity`, `UNIQUE(product_id, warehouse_id)`.
5. **`purchase_orders`**: `purchase_id` (PK), `supplier_id` (FK), `warehouse_id` (FK), `order_date`, `total_amount`.
6. **`purchase_items`**: `purchase_item_id` (PK), `purchase_id` (FK), `product_id` (FK), `quantity`, `price`.
7. **`sales`**: `sale_id` (PK), `product_id` (FK), `warehouse_id` (FK), `customer_name`, `quantity`, `sale_price`, `sale_date`.

### Entity Relationships:
```text
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
```

---

## ⚙️ Step-by-Step Installation & Setup

### Step 1: Open the Project in VS Code
1. Open **VS Code**.
2. Click **File > Open Folder...** and select:
   `C:\Users\HP\Desktop\Inventory Management System`

---

### Step 2: Open a Terminal in VS Code
In VS Code, press `` Ctrl + ` `` (or select **Terminal > New Terminal** from the top menu).

---

### Step 3: (Optional) Create & Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# OR activate on Windows (Command Prompt)
venv\Scripts\activate.bat
```

---

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```
This installs `Flask`, `mysql-connector-python`, and `python-dotenv`.

---

### Step 5: Configure Your MySQL Credentials
Open either the **`.env`** file or **`config.py`** in VS Code.

Set your MySQL username and password:
```ini
# .env file
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=inventory_db
MYSQL_PORT=3306
```

> 💡 **Where is my MySQL password?**
> This is the password you chose when installing MySQL Server or the password you type when logging into **MySQL Workbench**. If your root user has no password, leave `MYSQL_PASSWORD=` empty.

---

### Step 6: Setup MySQL Database & Sample Seed Data

You can set up the database in **either of two easy ways**:

#### Option A: Using the Automatic Python Initializer (Recommended)
Once your password is set in `.env` or `config.py`, run:
```bash
python init_db.py
```
This will automatically connect to MySQL, create `inventory_db`, build all 7 tables, and populate sample products, suppliers, warehouses, stock, purchases, and sales.

#### Option B: Using MySQL Workbench
1. Open **MySQL Workbench** and connect to your Local Instance.
2. Click **File > Open SQL Script...** and select `database/inventory.sql`.
3. Click the ⚡ **Execute** button (or press `Ctrl + Shift + Enter`).
4. In the left Navigator pane, right-click and choose **Refresh All**. You will see `inventory_db` with all tables populated!

---

### Step 7: Run the Flask Application
```bash
python app.py
```

You will see output in the terminal:
```text
============================================================
 Starting Inventory Management System...
 Access in your browser at: http://127.0.0.1:5000
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 8: Open the Website in Your Browser
Open Chrome, Edge, or Firefox and go to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Comprehensive Feature Testing Checklist

Follow these 12 test scenarios to verify every feature of your college project:

| Test # | Action | Expected Result |
| :--- | :--- | :--- |
| **Test 1** | Go to **Products** > Click **+ Add Product** > Enter name "Webcam 1080p", category "Electronics", price 2500, min stock 5 > Click Add. | Product appears in table and is stored in MySQL `products` table. |
| **Test 2** | Click **Edit** on "Webcam 1080p" > Change price to 2200 > Click Save Changes. | Price updates in table and in MySQL. |
| **Test 3** | Go to **Suppliers** > Click **+ Add Supplier** > Add "Delta Supplies", phone, email > Click Add. | Supplier appears in table and is stored in MySQL `suppliers` table. |
| **Test 4** | Go to **Warehouses** > Click **+ Add Warehouse** > Add "South Distribution Hub", location "Chennai" > Click Add. | Warehouse appears in table and is stored in MySQL `warehouses` table. |
| **Test 5** | Go to **Stock** > Filter by warehouse or view all items. | Table shows Product, Warehouse, Quantity, Minimum Stock, and Status. |
| **Test 6** | Go to **Purchases** > Click **+ New Purchase Order** > Select Supplier "ABC Electronics", Warehouse "Main Warehouse", Product "Laptop", Quantity 10, Price 55000 > Save. | Purchase order is saved in MySQL (`purchase_orders` & `purchase_items`). Laptop stock in Main Warehouse automatically increases by 10! |
| **Test 7** | Go to **Sales** > Click **+ New Sale Order** > Select Product "Laptop", Warehouse "Main Warehouse", Customer "Vikram Rao", Quantity 2, Price 58000 > Submit. | Sale is recorded in MySQL `sales` table. Laptop stock automatically decreases by 2! |
| **Test 8** | Try creating a Sale for "Keyboard" from "Main Warehouse" with Quantity **100** (more than available stock). | System blocks the sale and displays: **"Insufficient stock available. (Requested: 100, Available in this warehouse: X)"**. |
| **Test 9** | On the **Stock** page, find "Mouse" and manually update its quantity to **2** (below its minimum stock of 15). | Status badge turns 🔴 **LOW STOCK**. Dashboard alert counter increases! |
| **Test 10** | Open the **Reports** page. Look at **Low Stock Report**. | Displays only items where `quantity <= minimum_stock`. Query runs directly against MySQL. |
| **Test 11** | Look at **Supplier-wise Purchase Report** on the Reports page. | Shows Supplier Name, Product Name, and Total Purchased Quantity aggregated with MySQL `JOIN` and `GROUP BY`. |
| **Test 12** | Press `Ctrl + C` in the VS Code terminal to stop Flask. Restart it with `python app.py`. Refresh browser. | All records remain completely intact because they are saved in MySQL! |

---

## ❓ Common Errors & Troubleshooting

### 1. `Error 1045 (28000): Access denied for user 'root'@'localhost'`
- **Cause**: The password in `.env` or `config.py` does not match your MySQL Server root password.
- **Fix**: Open `.env`, set `MYSQL_PASSWORD=your_actual_password`, and save.

### 2. `Can't connect to MySQL server on 'localhost:3306'`
- **Cause**: MySQL Windows service is stopped.
- **Fix**:
  1. Press `Win + R`, type `services.msc`, and press Enter.
  2. Find **MySQL80** (or similar MySQL service).
  3. Right-click and choose **Start**.

### 3. `1049 (42000): Unknown database 'inventory_db'`
- **Cause**: The database schema has not been imported yet.
- **Fix**: Run `python init_db.py` OR open `database/inventory.sql` in MySQL Workbench and execute it.

### 4. `Cannot delete this product because it has linked stock, purchases, or sales records`
- **Cause**: Foreign key relational integrity protects against orphaned records.
- **Fix**: This is an intended safety feature. You must remove linked sales/stock records before deleting a master entity.

---

## 🎓 BTech College Viva Questions & Answers

### Q1: What architecture does this project follow?
> **Answer**: The project follows the **MVC (Model-View-Controller)** design pattern using Flask Blueprints.
> - **Model**: MySQL relational schema (`inventory_db`) managing persistent entity tables and relational integrity.
> - **View**: Jinja2 HTML5 templates with clean CSS3 for user interaction and responsive layouts.
> - **Controller**: Python Flask blueprints (`routes/*.py`) that handle HTTP requests, input validation, transaction management, and business logic.

### Q2: How does the Purchase and Sale logic maintain data consistency?
> **Answer**: 
> - For **Purchases**, a database transaction creates both the purchase order header (`purchase_orders`) and line item (`purchase_items`), and immediately updates the `stock` table using an upsert (`INSERT ... ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)`). If any query fails, `conn.rollback()` ensures no inconsistent data is stored.
> - For **Sales**, the system uses `SELECT quantity FROM stock ... FOR UPDATE` to lock and read current stock. If available stock is less than the requested quantity, the transaction is rejected immediately. If sufficient, the sale record is inserted and stock is decremented in the same transaction.

### Q3: Why is MySQL used instead of SQLite or browser storage?
> **Answer**: MySQL provides enterprise-grade ACID transactions, strict foreign key constraints (`ON DELETE RESTRICT`), high concurrency support, network accessibility, and proper relational JOIN performance, making it suitable for multi-warehouse inventory systems.

### Q4: How is Low Stock detected?
> **Answer**: A SQL query compares the current quantity in the `stock` table with the `minimum_stock` threshold set in the `products` table:
> ```sql
> SELECT * FROM stock s 
> JOIN products p ON s.product_id = p.product_id 
> WHERE s.quantity <= p.minimum_stock;
> ```
> If `quantity <= minimum_stock`, the status is displayed as 🔴 **LOW STOCK**; otherwise, 🟢 **IN STOCK**.
