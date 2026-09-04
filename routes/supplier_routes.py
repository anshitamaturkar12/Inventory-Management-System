from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error, IntegrityError

supplier_bp = Blueprint('suppliers', __name__)

@supplier_bp.route('/suppliers')
def list_suppliers():
    """Display all suppliers or filtered by name search."""
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('suppliers.html', suppliers=[], search_query=search_query)

    try:
        cursor = conn.cursor(dictionary=True)
        if search_query:
            sql = "SELECT * FROM suppliers WHERE supplier_name LIKE %s ORDER BY supplier_id DESC"
            cursor.execute(sql, (f"%{search_query}%",))
        else:
            cursor.execute("SELECT * FROM suppliers ORDER BY supplier_id DESC")
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('suppliers.html', suppliers=suppliers, search_query=search_query)
    except Error as e:
        flash(f"Error fetching suppliers: {e}", "danger")
        if conn:
            conn.close()
        return render_template('suppliers.html', suppliers=[], search_query=search_query)


@supplier_bp.route('/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    """Add a new supplier to MySQL."""
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()

        if not supplier_name:
            flash("Supplier name cannot be empty.", "warning")
            return render_template('add_supplier.html', supplier_name=supplier_name, phone=phone, email=email, address=address)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template('add_supplier.html')

        try:
            cursor = conn.cursor()
            sql = "INSERT INTO suppliers (supplier_name, phone, email, address) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (supplier_name, phone, email, address))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Supplier '{supplier_name}' added successfully!", "success")
            return redirect(url_for('suppliers.list_suppliers'))
        except Error as e:
            conn.rollback()
            conn.close()
            flash(f"Failed to add supplier: {e}", "danger")
            return render_template('add_supplier.html', supplier_name=supplier_name, phone=phone, email=email, address=address)

    return render_template('add_supplier.html')


@supplier_bp.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    """Edit an existing supplier."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('suppliers.list_suppliers'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()

        if not supplier_name:
            flash("Supplier name cannot be empty.", "warning")
            return redirect(url_for('suppliers.edit_supplier', supplier_id=supplier_id))

        try:
            sql = """
                UPDATE suppliers 
                SET supplier_name = %s, phone = %s, email = %s, address = %s 
                WHERE supplier_id = %s
            """
            cursor.execute(sql, (supplier_name, phone, email, address, supplier_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Supplier '{supplier_name}' updated successfully!", "success")
            return redirect(url_for('suppliers.list_suppliers'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update supplier: {e}", "danger")
            return redirect(url_for('suppliers.edit_supplier', supplier_id=supplier_id))

    cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close()
    conn.close()

    if not supplier:
        flash("Supplier not found.", "warning")
        return redirect(url_for('suppliers.list_suppliers'))

    return render_template('edit_supplier.html', supplier=supplier)


@supplier_bp.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    """Delete a supplier safely."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('suppliers.list_suppliers'))

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Supplier deleted successfully!", "success")
    except IntegrityError:
        conn.rollback()
        conn.close()
        flash("Cannot delete this supplier because there are purchase orders linked to them.", "danger")
    except Error as e:
        conn.rollback()
        conn.close()
        flash(f"Error deleting supplier: {e}", "danger")

    return redirect(url_for('suppliers.list_suppliers'))
