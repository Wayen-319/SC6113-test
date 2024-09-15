from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('dapp.db')
    conn.row_factory = sqlite3.Row
    return conn

# 主页面重定向
@app.route('/')
def index():
    return redirect(url_for('register'))

# 注册页面和处理逻辑
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', message='Passwords do not match!')

        # 检查用户名是否已经存在
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if existing_user:
            conn.close()
            return render_template('register.html', message='Username already exists. Please choose a different one.')

        # 哈希密码
        hashed_password = generate_password_hash(password)

        # 插入数据库
        try:
            conn.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            
            # 注册成功后重定向到 main 页面
            return redirect(url_for('main'))
        finally:
            conn.close()

    return render_template('register.html')

# 登录页面和处理逻辑
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            return render_template('login.html', message='Invalid username or password.')

    return render_template('login.html')

@app.route('/main',methods=["get","post"])
def main():
    r = request.form.get("q")
    current_time = datetime.datetime.now()
    conn = sqlite3.connect('dapp.db')
    c = conn.cursor()
    c.execute("insert into user values (?, ?)", (r, current_time))
    conn.commit()
    c.close()
    conn.close()
    return render_template('main.html',r=r)

@app.route('/store_money',methods=["get","post"])
def store_money():
    return render_template('store_money.html')

@app.route('/transfer_money',methods=["get","post"])
def transfer_money():
    return render_template('transfer_money.html')

@app.route('/admin',methods=["get","post"])
def admin():
    return render_template('admin.html')

@app.route('/viewDB',methods=["get","post"])
def viewDB():
    conn = sqlite3.connect('dapp.db')
    c = conn.cursor()
    c.execute("select * from user")
    r = ""
    for row in c:
        r += str(row) + "\n"
    conn.commit()
    c.close()
    conn.close()
    return render_template('viewDB.html',r=r)

@app.route('/delDB',methods=["get","post"])
def delDB():
    conn = sqlite3.connect('dapp.db')
    c = conn.cursor()
    c.execute("delete from user")
    conn.commit()
    c.close()
    conn.close()
    return render_template('deleteDB.html')

if __name__=='__main__':
    app.run()
