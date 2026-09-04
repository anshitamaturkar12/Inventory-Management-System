from flask import Blueprint, render_template, request, redirect, url_for, flash
from config import get_db_connection
from mysql.connector import Error, IntegrityError

product_bp = Blueprint('products', __name__)

@product_bp.route('/products')
def list_products():
    """Display all products or filtered by search term."""
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please check MySQL settings.", "danger")
        return render_template('products.html', products=[], search_query=search_query)

    try:
        cursor = conn.cursor(dictionary=True)
        if search_query:
            sql = """
                SELECT * FROM products 
                WHERE product_name LIKE %s OR category LIKE %s
                ORDER BY product_id DESC
            """
            like_param = f"%{search_query}%"
            cursor.execute(sql, (like_param, like_param))
        else:
            cursor.execute("SELECT * FROM products ORDER BY product_id DESC")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('products.html', products=products, search_query=search_query)
    except Error as e:
        flash(f"Error fetching products: {e}", "danger")
        if conn:
            conn.close()
        return render_template('products.html', products=[], search_query=search_query)


@product_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add a new product to MySQL."""
    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', '').strip()
        price_str = request.form.get('price', '').strip()
        min_stock_str = request.form.get('minimum_stock', '').strip()

        # Validation
        if not product_name or not category:
            flash("Product name and category cannot be empty.", "warning")
            return render_template('add_product.html', product_name=product_name, category=category, price=price_str, minimum_stock=min_stock_str)

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            flash("Price must be a valid non-negative number.", "warning")
            return render_template('add_product.html', product_name=product_name, category=category, price=price_str, minimum_stock=min_stock_str)

        try:
            minimum_stock = int(min_stock_str)
            if minimum_stock < 0:
                raise ValueError()
        except ValueError:
            flash("Minimum stock must be a non-negative integer.", "warning")
            return render_template('add_product.html', product_name=product_name, category=category, price=price_str, minimum_stock=min_stock_str)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template('add_product.html')

        try:
            cursor = conn.cursor()
            sql = "INSERT INTO products (product_name, category, price, minimum_stock) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (product_name, category, price, minimum_stock))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Product '{product_name}' added successfully!", "success")
            return redirect(url_for('products.list_products'))
        except Error as e:
            conn.rollback()
            conn.close()
            flash(f"Failed to add product: {e}", "danger")
            return render_template('add_product.html')

    return render_template('add_product.html')


@product_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit an existing product."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('products.list_products'))

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', '').strip()
        price_str = request.form.get('price', '').strip()
        min_stock_str = request.form.get('minimum_stock', '').strip()

        # Validation
        if not product_name or not category:
            flash("Product name and category cannot be empty.", "warning")
            return redirect(url_for('products.edit_product', product_id=product_id))

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            flash("Price must be a valid non-negative number.", "warning")
            return redirect(url_for('products.edit_product', product_id=product_id))

        try:
            minimum_stock = int(min_stock_str)
            if minimum_stock < 0:
                raise ValueError()
        except ValueError:
            flash("Minimum stock must be a non-negative integer.", "warning")
            return redirect(url_for('products.edit_product', product_id=product_id))

        try:
            update_sql = """
                UPDATE products 
                SET product_name = %s, category = %s, price = %s, minimum_stock = %s 
                WHERE product_id = %s
            """
            cursor.execute(update_sql, (product_name, category, price, minimum_stock, product_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Product '{product_name}' updated successfully!", "success")
            return redirect(url_for('products.list_products'))
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update product: {e}", "danger")
            return redirect(url_for('products.edit_product', product_id=product_id))

    # GET request - fetch product details
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for('products.list_products'))

    return render_template('edit_product.html', product=product)


@product_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product safely from MySQL."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('products.list_products'))

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Product deleted successfully!", "success")
    except IntegrityError:
        conn.rollback()
        conn.close()
        flash("Cannot delete this product because it has linked stock, purchases, or sales records.", "danger")
    except Error as e:
        conn.rollback()
        conn.close()
        flash(f"Error deleting product: {e}", "danger")

    return redirect(url_for('products.list_products'))
