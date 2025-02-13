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

if __name__ == '__main__':
    app.run(debug=True)
