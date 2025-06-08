
from flask import Flask, request, render_template, redirect, url_for, session, abort
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = 'very_secret_key_hojreh'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'hojreh_data.json'


def check_owner(shop_id):
    if 'shop_id' not in session or session['shop_id'] != shop_id:
        abort(403)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['POST'])
def register():
    shop_name = request.form.get('shop_name')
    phone = request.form.get('phone')
    main_category = request.form.get('main_category')
    sub_category = request.form.get('sub_category')
    username = request.form.get('username')
    password = request.form.get('password')

    new_shop = {
        "shop_name": shop_name,
        "phone": phone,
        "category_main": main_category,
        "category_sub": sub_category,
        "username": username,
        "password": password
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_shop)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return f"✅ حجره با نام {shop_name} ثبت شد!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        for i, shop in enumerate(data):
            if shop['username'] == username and shop['password'] == password:
                session['shop_id'] = i
                return redirect(url_for('show_products', shop_id=i))

        return render_template('login.html', error="نام کاربری یا رمز اشتباه است.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/shops')
def show_shops():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    return render_template("shops.html", shops=data)


@app.route('/shop/<int:shop_id>')
def shop_detail(shop_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    if 0 <= shop_id < len(data):
        shop = data[shop_id]
        return render_template("shop_detail.html", shop=shop)
    else:
        return "⛔️ حجره‌ای با این شناسه پیدا نشد", 404


@app.route('/edit/<int:shop_id>', methods=['GET', 'POST'])
def edit_shop(shop_id):
    check_owner(shop_id)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        return "⛔ فایل داده‌ها پیدا نشد", 404

    if 0 <= shop_id < len(data):
        if request.method == 'POST':
            data[shop_id]['shop_name'] = request.form.get('shop_name')
            data[shop_id]['phone'] = request.form.get('phone')
            data[shop_id]['category_main'] = request.form.get('main_category')
            data[shop_id]['category_sub'] = request.form.get('sub_category')

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return render_template("edit_success.html", shop=data[shop_id])
        else:
            return render_template("edit.html", shop=data[shop_id], shop_id=shop_id)
    else:
        return "⛔ شناسه حجره نامعتبر است", 404


@app.route('/delete/<int:shop_id>')
def delete_shop(shop_id):
    check_owner(shop_id)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    if 0 <= shop_id < len(data):
        deleted = data.pop(shop_id)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return render_template("delete_success.html", shop_name=deleted['shop_name'])
    else:
        return "⛔ شناسه نامعتبر", 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
