from flask import Flask, render_template, flash
from config import Config, get_db_connection
from mysql.connector import Error

# Import route blueprints
from routes.product_routes import product_bp
from routes.supplier_routes import supplier_bp
from routes.warehouse_routes import warehouse_bp
from routes.stock_routes import stock_bp
from routes.purchase_routes import purchase_bp
from routes.sales_routes import sales_bp
from routes.report_routes import report_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(product_bp)
app.register_blueprint(supplier_bp)
app.register_blueprint(warehouse_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(report_bp)


@app.route('/')
@app.route('/dashboard')
def dashboard():
    """
    Main Dashboard View
    Queries MySQL for overall inventory KPIs and recent transactions.
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database. Please verify MySQL service is running and credentials in config.py or .env are correct.", "danger")
        return render_template(
            'dashboard.html',
            total_products=0,
            total_suppliers=0,
            total_warehouses=0,
            total_stock=0,
            low_stock_count=0,
            low_stock_items=[],
            recent_purchases=[],
            recent_sales=[]
        )

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Total Products
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total_products = cursor.fetchone()['total']

        # 2. Total Suppliers
        cursor.execute("SELECT COUNT(*) AS total FROM suppliers")
        total_suppliers = cursor.fetchone()['total']

        # 3. Total Warehouses
        cursor.execute("SELECT COUNT(*) AS total FROM warehouses")
        total_warehouses = cursor.fetchone()['total']

        # 4. Total Stock
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) AS total FROM stock")
        total_stock = cursor.fetchone()['total']

        # 5. Low Stock Count
        cursor.execute("""
            SELECT COUNT(*) AS total 
            FROM stock s 
            JOIN products p ON s.product_id = p.product_id 
            WHERE s.quantity <= p.minimum_stock
        """)
        low_stock_count = cursor.fetchone()['total']

        # 6. Dashboard Low Stock Alert Items
        cursor.execute("""
            SELECT 
                p.product_name,
                w.warehouse_name,
                s.quantity AS current_stock,
                p.minimum_stock,
                CASE 
                    WHEN s.quantity <= p.minimum_stock THEN 'LOW STOCK'
                    ELSE 'IN STOCK'
                END AS stock_status
            FROM stock s
            JOIN products p ON s.product_id = p.product_id
            JOIN warehouses w ON s.warehouse_id = w.warehouse_id
            WHERE s.quantity <= p.minimum_stock
            ORDER BY s.quantity ASC
            LIMIT 5
        """)
        low_stock_items = cursor.fetchall()

        # 7. Recent Purchases (last 5)
        cursor.execute("""
            SELECT 
                po.purchase_id,
                s.supplier_name,
                p.product_name,
                pi.quantity,
                po.total_amount,
                po.order_date
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.supplier_id
            JOIN purchase_items pi ON po.purchase_id = pi.purchase_id
            JOIN products p ON pi.product_id = p.product_id
            ORDER BY po.purchase_id DESC
            LIMIT 5
        """)
        recent_purchases = cursor.fetchall()

        # 8. Recent Sales (last 5)
        cursor.execute("""
            SELECT 
                s.sale_id,
                p.product_name,
                s.customer_name,
                s.quantity,
                (s.quantity * s.sale_price) AS total_amount,
                s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            ORDER BY s.sale_id DESC
            LIMIT 5
        """)
        recent_sales = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            'dashboard.html',
            total_products=total_products,
            total_suppliers=total_suppliers,
            total_warehouses=total_warehouses,
            total_stock=total_stock,
            low_stock_count=low_stock_count,
            low_stock_items=low_stock_items,
            recent_purchases=recent_purchases,
            recent_sales=recent_sales
        )
    except Error as e:
        flash(f"Database query error: {e}", "danger")
        if conn:
            conn.close()
        return render_template(
            'dashboard.html',
            total_products=0,
            total_suppliers=0,
            total_warehouses=0,
            total_stock=0,
            low_stock_count=0,
            low_stock_items=[],
            recent_purchases=[],
            recent_sales=[]
        )


@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', not_found=True), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', server_error=True), 500


if __name__ == '__main__':
    # Run application locally
    print("=" * 60)
    print(" Starting Inventory Management System...")
    print(" Access in your browser at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
