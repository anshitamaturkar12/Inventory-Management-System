from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/stock')
def list_stock():
    """Display stock list with optional warehouse filter."""
    warehouse_filter = request.args.get('warehouse_id', '').strip()
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('stock.html', stock_items=[], warehouses=[], selected_warehouse=warehouse_filter)

    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch warehouses for dropdown filter
        cursor.execute("SELECT * FROM warehouses ORDER BY warehouse_name ASC")
        warehouses = cursor.fetchall()

        # Fetch stock records joined with products and warehouses
        if warehouse_filter and warehouse_filter.isdigit():
            sql = """
                SELECT 
                    s.stock_id,
                    s.product_id,
                    s.warehouse_id,
                    p.product_name,
                    p.category,
                    p.minimum_stock,
                    w.warehouse_name,
                    s.quantity
                FROM stock s
                JOIN products p ON s.product_id = p.product_id
                JOIN warehouses w ON s.warehouse_id = w.warehouse_id
                WHERE s.warehouse_id = %s
                ORDER BY p.product_name ASC
            """
            cursor.execute(sql, (int(warehouse_filter),))
        else:
            sql = """
                SELECT 
                    s.stock_id,
                    s.product_id,
                    s.warehouse_id,
                    p.product_name,
                    p.category,
                    p.minimum_stock,
                    w.warehouse_name,
                    s.quantity
                FROM stock s
                JOIN products p ON s.product_id = p.product_id
                JOIN warehouses w ON s.warehouse_id = w.warehouse_id
                ORDER BY w.warehouse_name ASC, p.product_name ASC
            """
            cursor.execute(sql)

        stock_items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('stock.html', stock_items=stock_items, warehouses=warehouses, selected_warehouse=warehouse_filter)
    except Error as e:
        flash(f"Error fetching stock: {e}", "danger")
        if conn:
            conn.close()
        return render_template('stock.html', stock_items=[], warehouses=[], selected_warehouse=warehouse_filter)


@stock_bp.route('/stock/update', methods=['POST'])
def update_stock():
    """Directly update quantity for an existing stock record."""
    stock_id_str = request.form.get('stock_id', '').strip()
    quantity_str = request.form.get('quantity', '').strip()

    if not stock_id_str or not quantity_str:
        flash("Stock ID and Quantity are required.", "warning")
        return redirect(url_for('stock.list_stock'))

    try:
        quantity = int(quantity_str)
        if quantity < 0:
            flash("Stock quantity cannot be negative.", "warning")
            return redirect(url_for('stock.list_stock'))
    except ValueError:
        flash("Invalid quantity value.", "warning")
        return redirect(url_for('stock.list_stock'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('stock.list_stock'))

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE stock SET quantity = %s WHERE stock_id = %s", (quantity, int(stock_id_str)))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Stock quantity updated successfully in MySQL!", "success")
    except Error as e:
        conn.rollback()
        conn.close()
        flash(f"Error updating stock: {e}", "danger")

    return redirect(url_for('stock.list_stock'))


@stock_bp.route('/stock/add', methods=['POST'])
def add_initial_stock():
    """Add new stock mapping for a product in a warehouse."""
    product_id_str = request.form.get('product_id', '').strip()
    warehouse_id_str = request.form.get('warehouse_id', '').strip()
    quantity_str = request.form.get('quantity', '0').strip()

    if not product_id_str or not warehouse_id_str:
        flash("Please select both a product and a warehouse.", "warning")
        return redirect(url_for('stock.list_stock'))

    try:
        product_id = int(product_id_str)
        warehouse_id = int(warehouse_id_str)
        quantity = int(quantity_str)
        if quantity < 0:
            flash("Quantity cannot be negative.", "warning")
            return redirect(url_for('stock.list_stock'))
    except ValueError:
        flash("Invalid numeric value provided.", "warning")
        return redirect(url_for('stock.list_stock'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('stock.list_stock'))

    try:
        cursor = conn.cursor()
        # INSERT or UPDATE if already exists (ON DUPLICATE KEY UPDATE)
        sql = """
            INSERT INTO stock (product_id, warehouse_id, quantity) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
        """
        cursor.execute(sql, (product_id, warehouse_id, quantity))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Stock recorded successfully!", "success")
    except Error as e:
        conn.rollback()
        conn.close()
        flash(f"Error recording stock: {e}", "danger")

    return redirect(url_for('stock.list_stock'))
