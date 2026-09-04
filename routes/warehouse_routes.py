from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error, IntegrityError

warehouse_bp = Blueprint('warehouses', __name__)

@warehouse_bp.route('/warehouses')
def list_warehouses():
    """Display all warehouses."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('warehouses.html', warehouses=[])

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM warehouses ORDER BY warehouse_id ASC")
        warehouses = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('warehouses.html', warehouses=warehouses)
    except Error as e:
        flash(f"Error fetching warehouses: {e}", "danger")
        if conn:
            conn.close()
        return render_template('warehouses.html', warehouses=[])


@warehouse_bp.route('/warehouses/add', methods=['GET', 'POST'])
def add_warehouse():
    """Add a new warehouse."""
    if request.method == 'POST':
        warehouse_name = request.form.get('warehouse_name', '').strip()
        location = request.form.get('location', '').strip()

        if not warehouse_name:
            flash("Warehouse name cannot be empty.", "warning")
            return render_template('add_warehouse.html', warehouse_name=warehouse_name, location=location)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template('add_warehouse.html')

        try:
            cursor = conn.cursor()
            sql = "INSERT INTO warehouses (warehouse_name, location) VALUES (%s, %s)"
            cursor.execute(sql, (warehouse_name, location))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Warehouse '{warehouse_name}' added successfully!", "success")
            return redirect(url_for('warehouses.list_warehouses'))
        except Error as e:
            conn.rollback()
            conn.close()
            flash(f"Failed to add warehouse: {e}", "danger")
            return render_template('add_warehouse.html', warehouse_name=warehouse_name, location=location)

    return render_template('add_warehouse.html')


@warehouse_bp.route('/warehouses/edit/<int:warehouse_id>', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit an existing warehouse."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('warehouses.list_warehouses'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        warehouse_name = request.form.get('warehouse_name', '').strip()
        location = request.form.get('location', '').strip()

        if not warehouse_name:
            flash("Warehouse name cannot be empty.", "warning")
            return redirect(url_for('warehouses.edit_warehouse', warehouse_id=warehouse_id))

        try:
            sql = "UPDATE warehouses SET warehouse_name = %s, location = %s WHERE warehouse_id = %s"
            cursor.execute(sql, (warehouse_name, location, warehouse_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Warehouse '{warehouse_name}' updated successfully!", "success")
            return redirect(url_for('warehouses.list_warehouses'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update warehouse: {e}", "danger")
            return redirect(url_for('warehouses.edit_warehouse', warehouse_id=warehouse_id))

    cursor.execute("SELECT * FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
    warehouse = cursor.fetchone()
    cursor.close()
    conn.close()

    if not warehouse:
        flash("Warehouse not found.", "warning")
        return redirect(url_for('warehouses.list_warehouses'))

    return render_template('edit_warehouse.html', warehouse=warehouse)


@warehouse_bp.route('/warehouses/delete/<int:warehouse_id>', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete warehouse safely."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('warehouses.list_warehouses'))

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Warehouse deleted successfully!", "success")
    except IntegrityError:
        conn.rollback()
        conn.close()
        flash("Cannot delete this warehouse because it contains stock or recorded sales.", "danger")
    except Error as e:
        conn.rollback()
        conn.close()
        flash(f"Error deleting warehouse: {e}", "danger")

    return redirect(url_for('warehouses.list_warehouses'))
