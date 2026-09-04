from flask import Blueprint, render_template, request, flash
from config import get_db_connection
from mysql.connector import Error

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports')
def view_reports():
    """Render Reports page with Low Stock, Supplier-wise, and Warehouse-wise reports."""
    supplier_filter = request.args.get('supplier_id', '').strip()

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('reports.html', low_stock=[], supplier_report=[], warehouse_report=[], suppliers=[], selected_supplier=supplier_filter)

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Fetch suppliers for dropdown filter
        cursor.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC")
        suppliers = cursor.fetchall()

        # 2. LOW STOCK REPORT: Actual MySQL query where stock.quantity <= products.minimum_stock
        low_stock_sql = """
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                w.warehouse_name,
                s.quantity AS current_stock,
                p.minimum_stock
            FROM stock s
            JOIN products p ON s.product_id = p.product_id
            JOIN warehouses w ON s.warehouse_id = w.warehouse_id
            WHERE s.quantity <= p.minimum_stock
            ORDER BY s.quantity ASC
        """
        cursor.execute(low_stock_sql)
        low_stock = cursor.fetchall()

        # 3. SUPPLIER-WISE INVENTORY REPORT: Joins across suppliers, purchase_orders, purchase_items, products
        if supplier_filter and supplier_filter.isdigit():
            supplier_report_sql = """
                SELECT 
                    s.supplier_id,
                    s.supplier_name,
                    p.product_name,
                    p.category,
                    SUM(pi.quantity) AS total_purchased_quantity,
                    SUM(pi.quantity * pi.price) AS total_spent
                FROM suppliers s
                JOIN purchase_orders po ON s.supplier_id = po.supplier_id
                JOIN purchase_items pi ON po.purchase_id = pi.purchase_id
                JOIN products p ON pi.product_id = p.product_id
                WHERE s.supplier_id = %s
                GROUP BY s.supplier_id, s.supplier_name, p.product_id, p.product_name, p.category
                ORDER BY s.supplier_name ASC, total_purchased_quantity DESC
            """
            cursor.execute(supplier_report_sql, (int(supplier_filter),))
        else:
            supplier_report_sql = """
                SELECT 
                    s.supplier_id,
                    s.supplier_name,
                    p.product_name,
                    p.category,
                    SUM(pi.quantity) AS total_purchased_quantity,
                    SUM(pi.quantity * pi.price) AS total_spent
                FROM suppliers s
                JOIN purchase_orders po ON s.supplier_id = po.supplier_id
                JOIN purchase_items pi ON po.purchase_id = pi.purchase_id
                JOIN products p ON pi.product_id = p.product_id
                GROUP BY s.supplier_id, s.supplier_name, p.product_id, p.product_name, p.category
                ORDER BY s.supplier_name ASC, total_purchased_quantity DESC
            """
            cursor.execute(supplier_report_sql)
        supplier_report = cursor.fetchall()

        # 4. WAREHOUSE-WISE STOCK REPORT
        warehouse_report_sql = """
            SELECT 
                w.warehouse_name,
                p.product_name,
                p.category,
                s.quantity
            FROM stock s
            JOIN warehouses w ON s.warehouse_id = w.warehouse_id
            JOIN products p ON s.product_id = p.product_id
            ORDER BY w.warehouse_name ASC, p.product_name ASC
        """
        cursor.execute(warehouse_report_sql)
        warehouse_report = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            'reports.html',
            low_stock=low_stock,
            supplier_report=supplier_report,
            warehouse_report=warehouse_report,
            suppliers=suppliers,
            selected_supplier=supplier_filter
        )
    except Error as e:
        flash(f"Error generating reports: {e}", "danger")
        if conn:
            conn.close()
        return render_template('reports.html', low_stock=[], supplier_report=[], warehouse_report=[], suppliers=[], selected_supplier=supplier_filter)
