from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "cafe_app.db"

# データベース接続
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 辞書形式でデータ取得
    return conn

# 商品登録ページ
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO PRODUCTS (NAME, DESCRIPTION, CATEGORY, PRICE) VALUES (?, ?, ?, ?)",
                       (name, description, category, price))
        conn.commit()
        conn.close()

        return redirect(url_for('add_product'))  # 登録後に同じページにリダイレクト

    return render_template('add_product.html')

@app.route('/products')
def product_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PRODUCTS")
    products = cursor.fetchall()
    conn.close()

    return render_template('products.html', products=products)

@app.route('/stock_entry', methods=['GET', 'POST'])
def stock_entry():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 商品リストとユーザーリストを取得
    cursor.execute("SELECT ID, NAME FROM PRODUCTS")
    products = cursor.fetchall()
    
    cursor.execute("SELECT ID, USERNAME FROM USERS")
    users = cursor.fetchall()

    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        quantity = request.form['quantity']
        entry_type = request.form['type']  # 入庫 or 出庫
        note = request.form['note']
        timestamp = datetime.now()

        # STOCK_HISTORY に登録
        cursor.execute("""
            INSERT INTO STOCK_HISTORY (PRODUCT_ID, USER_ID, QUANTITY, TYPE, TIMESTAMP, NOTE)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, user_id, quantity, entry_type, timestamp, note))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('stock_entry'))  # 登録後にリダイレクト

    conn.close()
    return render_template('stock_entry.html', products=products, users=users)

@app.route('/stock_history')
def stock_history():
    conn = get_db_connection()
    cursor = conn.cursor()

    # STOCK_HISTORYのデータを取得し、商品名とユーザー名を結合
    cursor.execute("""
        SELECT sh.ID, p.NAME AS PRODUCT_NAME, u.USERNAME, sh.QUANTITY, sh.TYPE, sh.TIMESTAMP, sh.NOTE
        FROM STOCK_HISTORY sh
        JOIN PRODUCTS p ON sh.PRODUCT_ID = p.ID
        JOIN USERS u ON sh.USER_ID = u.ID
        ORDER BY sh.TIMESTAMP DESC
    """)
    history = cursor.fetchall()
    conn.close()

    return render_template('stock_history.html', history=history)

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 各商品の最新の在庫数と最終更新日を取得
    cursor.execute("""
        SELECT p.NAME AS PRODUCT_NAME, 
               COALESCE(SUM(CASE WHEN sh.TYPE = '入庫' THEN sh.QUANTITY 
                                 WHEN sh.TYPE = '出庫' THEN -sh.QUANTITY 
                                 ELSE 0 END), 0) AS STOCK_QUANTITY,
               (SELECT MAX(TIMESTAMP) 
                FROM STOCK_HISTORY 
                WHERE PRODUCT_ID = p.ID) AS LAST_UPDATED
        FROM PRODUCTS p
        LEFT JOIN STOCK_HISTORY sh ON p.ID = sh.PRODUCT_ID
        GROUP BY p.ID
    """)
    inventory_data = cursor.fetchall()
    conn.close()

    return render_template('inventory.html', inventory=inventory_data)



if __name__ == '__main__':
    app.run(debug=True)
