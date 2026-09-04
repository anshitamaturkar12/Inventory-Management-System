from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error
from datetime import date

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales')
def list_sales():
    """Display sales history list."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('sales.html', sales=[])

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                s.sale_id,
                p.product_name,
                w.warehouse_name,
                s.customer_name,
                s.quantity,
                s.sale_price,
                (s.quantity * s.sale_price) AS total_revenue,
                s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            JOIN warehouses w ON s.warehouse_id = w.warehouse_id
            ORDER BY s.sale_id DESC
        """
        cursor.execute(sql)
        sales = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('sales.html', sales=sales)
    except Error as e:
        flash(f"Error fetching sales: {e}", "danger")
        if conn:
            conn.close()
        return render_template('sales.html', sales=[])


@sales_bp.route('/sales/add', methods=['GET', 'POST'])
def add_sale():
    """Create a new sale order with strict stock validation."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return redirect(url_for('sales.list_sales'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        product_id = request.form.get('product_id', '').strip()
        warehouse_id = request.form.get('warehouse_id', '').strip()
        customer_name = request.form.get('customer_name', '').strip()
        quantity_str = request.form.get('quantity', '').strip()
        price_str = request.form.get('sale_price', '').strip()
        sale_date = request.form.get('sale_date', '').strip()

        # Validation
        if not product_id or not warehouse_id:
            flash("Please select both Product and Warehouse.", "warning")
            return redirect(url_for('sales.add_sale'))

        if not customer_name:
            flash("Customer Name cannot be empty.", "warning")
            return redirect(url_for('sales.add_sale'))

        if not sale_date:
            sale_date = str(date.today())

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                flash("Sale quantity must be greater than zero.", "warning")
                return redirect(url_for('sales.add_sale'))
        except ValueError:
            flash("Invalid quantity value.", "warning")
            return redirect(url_for('sales.add_sale'))

        try:
            sale_price = float(price_str)
            if sale_price < 0:
                flash("Sale price cannot be negative.", "warning")
                return redirect(url_for('sales.add_sale'))
        except ValueError:
            flash("Invalid price value.", "warning")
            return redirect(url_for('sales.add_sale'))

        try:
            # 1. Check available stock in MySQL for this product in this warehouse
            check_stock_sql = """
                SELECT quantity FROM stock 
                WHERE product_id = %s AND warehouse_id = %s 
                FOR UPDATE
            """
            cursor.execute(check_stock_sql, (int(product_id), int(warehouse_id)))
            stock_row = cursor.fetchone()

            available_stock = stock_row['quantity'] if stock_row else 0

            # 2. Strict Check: If requested quantity > available stock, REJECT!
            if available_stock < quantity:
                conn.rollback()
                cursor.close()
                conn.close()
                flash(f"Insufficient stock available. (Requested: {quantity}, Available in this warehouse: {available_stock})", "danger")
                return redirect(url_for('sales.add_sale'))

            # 3. If enough stock exists, record sale
            insert_sale_sql = """
                INSERT INTO sales (product_id, warehouse_id, customer_name, quantity, sale_price, sale_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sale_sql, (int(product_id), int(warehouse_id), customer_name, quantity, sale_price, sale_date))
            sale_id = cursor.lastrowid

            # 4. Automatically decrease stock
            update_stock_sql = """
                UPDATE stock 
                SET quantity = quantity - %s 
                WHERE product_id = %s AND warehouse_id = %s
            """
            cursor.execute(update_stock_sql, (quantity, int(product_id), int(warehouse_id)))

            # Commit transaction
            conn.commit()
            cursor.close()
            conn.close()

            flash(f"Sale #{sale_id} completed successfully! Stock decreased by {quantity}.", "success")
            return redirect(url_for('sales.list_sales'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Error processing sale: {e}", "danger")
            return redirect(url_for('sales.add_sale'))

    # GET: fetch products and warehouses for dropdowns
    cursor.execute("SELECT product_id, product_name, price FROM products ORDER BY product_name ASC")
    products = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM warehouses ORDER BY warehouse_name ASC")
    warehouses = cursor.fetchall()

    cursor.close()
    conn.close()

    today_str = date.today().isoformat()
    return render_template('add_sale.html', products=products, warehouses=warehouses, today=today_str)
