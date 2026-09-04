from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error
from datetime import date

purchase_bp = Blueprint('purchases', __name__)

@purchase_bp.route('/purchases')
def list_purchases():
    """Display purchase history list."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('purchases.html', purchases=[])

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                po.purchase_id,
                s.supplier_name,
                p.product_name,
                w.warehouse_name,
                pi.quantity,
                pi.price,
                (pi.quantity * pi.price) AS total_cost,
                po.order_date
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.supplier_id
            JOIN warehouses w ON po.warehouse_id = w.warehouse_id
            JOIN purchase_items pi ON po.purchase_id = pi.purchase_id
            JOIN products p ON pi.product_id = p.product_id
            ORDER BY po.purchase_id DESC
        """
        cursor.execute(sql)
        purchases = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('purchases.html', purchases=purchases)
    except Error as e:
        flash(f"Error fetching purchases: {e}", "danger")
        if conn:
            conn.close()
        return render_template('purchases.html', purchases=[])


@purchase_bp.route('/purchases/add', methods=['GET', 'POST'])
def add_purchase():
    """Create a new purchase order and automatically increment warehouse stock."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return redirect(url_for('purchases.list_purchases'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', '').strip()
        product_id = request.form.get('product_id', '').strip()
        warehouse_id = request.form.get('warehouse_id', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        price_str = request.form.get('price', '').strip()
        order_date = request.form.get('order_date', '').strip()

        # Validation
        if not supplier_id or not product_id or not warehouse_id:
            flash("Please select Supplier, Product, and Warehouse.", "warning")
            return redirect(url_for('purchases.add_purchase'))

        if not order_date:
            order_date = str(date.today())

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                flash("Purchase quantity must be greater than zero.", "warning")
                return redirect(url_for('purchases.add_purchase'))
        except ValueError:
            flash("Invalid quantity entered.", "warning")
            return redirect(url_for('purchases.add_purchase'))

        try:
            price = float(price_str)
            if price < 0:
                flash("Purchase price cannot be negative.", "warning")
                return redirect(url_for('purchases.add_purchase'))
        except ValueError:
            flash("Invalid price entered.", "warning")
            return redirect(url_for('purchases.add_purchase'))

        total_amount = quantity * price

        try:
            # 1. Insert into purchase_orders
            cursor.execute(
                "INSERT INTO purchase_orders (supplier_id, warehouse_id, order_date, total_amount) VALUES (%s, %s, %s, %s)",
                (int(supplier_id), int(warehouse_id), order_date, total_amount)
            )
            purchase_id = cursor.lastrowid

            # 2. Insert into purchase_items
            cursor.execute(
                "INSERT INTO purchase_items (purchase_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (purchase_id, int(product_id), quantity, price)
            )

            # 3. Automatically increase stock for this product in this warehouse
            stock_sql = """
                INSERT INTO stock (product_id, warehouse_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """
            cursor.execute(stock_sql, (int(product_id), int(warehouse_id), quantity))

            # Commit the transaction
            conn.commit()
            cursor.close()
            conn.close()

            flash(f"Purchase order #{purchase_id} created successfully! Stock increased by {quantity}.", "success")
            return redirect(url_for('purchases.list_purchases'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to record purchase: {e}", "danger")
            return redirect(url_for('purchases.add_purchase'))

    # GET: fetch suppliers, products, and warehouses for form dropdowns
    cursor.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC")
    suppliers = cursor.fetchall()

    cursor.execute("SELECT product_id, product_name, price FROM products ORDER BY product_name ASC")
    products = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM warehouses ORDER BY warehouse_name ASC")
    warehouses = cursor.fetchall()

    cursor.close()
    conn.close()

    today_str = date.today().isoformat()
    return render_template('add_purchase.html', suppliers=suppliers, products=products, warehouses=warehouses, today=today_str)
