from flask import Flask, request, render_template, redirect, url_for, session, abort
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from datetime import datetime
import pytz
import jdatetime


app = Flask(__name__)
app.secret_key = 'very_secret_key_hojreh'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'hojreh_data.json'


def check_owner(shop_id):
    if 'shop_id' not in session or session['shop_id'] != shop_id:
        abort(403)


@app.route('/', methods=['GET'])
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
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    address = request.form.get('address')


    new_shop = {
        "shop_name": shop_name,
        "phone": phone,
        "category_main": main_category,
        "category_sub": sub_category,
        "username": username,
        "password": password,
        "latitude": latitude,
        "longitude": longitude,
        "address": address

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

        return render_template('login.html', error="نام کاربری یا رمز عبور اشتباه است.")

    return render_template('login.html')





@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/shops')
def show_shops():
    name_query = request.args.get('shop_name', '').strip()
    phone_query = request.args.get('phone', '').strip()
    subcat_query = request.args.get('sub_category', '').strip()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    filtered = []
    for shop in data:
        if name_query and name_query not in shop['shop_name']:
            continue
        if phone_query and phone_query not in shop['phone']:
            continue
        if subcat_query and subcat_query not in shop['category_sub']:
            continue
        filtered.append(shop)

    return render_template("shops.html", shops=filtered)






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





@app.route('/products/<int:shop_id>')
def show_products(shop_id):
    check_owner(shop_id)
    product_file = f'products_{shop_id}.json'
    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []
    return render_template("show_products.html", products=products, shop_id=shop_id)







@app.route('/product/<int:shop_id>', methods=['GET', 'POST'])
def add_product(shop_id):
    check_owner(shop_id)
    product_file = f'products_{shop_id}.json'

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        discount = request.form.get('discount') if request.form.get('has_discount') else None

        images = request.files.getlist('images')
        image_paths = []

        for image in images[:3]:
            if image.filename:
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                image_paths.append(filepath)

        new_product = {
            "product_name": product_name,
            "price": price,
            "discount": discount,
            "images": image_paths
        }

        if os.path.exists(product_file):
            with open(product_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
        else:
            products = []

        products.append(new_product)

        with open(product_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        return redirect(url_for('show_products', shop_id=shop_id))

    return render_template("add_product.html", shop_id=shop_id)






@app.route('/shop/<int:shop_id>/products')
def shop_store(shop_id):
    product_file = f'products_{shop_id}.json'

    name_query = request.args.get('name', '').strip()
    discount_only = request.args.get('discount_only') == 'on'
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    filtered = []
    for product in products:
        if name_query and name_query not in product['product_name']:
            continue
        if discount_only and not product.get('discount'):
            continue
        price = int(product['price']) if product['price'].isdigit() else 0
        if min_price and price < int(min_price):
            continue
        if max_price and price > int(max_price):
            continue
        filtered.append(product)

    return render_template("shop_store.html", products=filtered, shop_id=shop_id)






@app.route('/dashboard')
def dashboard():
    if 'shop_id' not in session:
        return redirect(url_for('login'))

    shop_id = session['shop_id']

    # خواندن اطلاعات حجره
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            shops = json.load(f)
            shop = shops[shop_id]
    else:
        return "⛔ اطلاعات حجره پیدا نشد", 404

    # خواندن محصولات
    product_file = f'products_{shop_id}.json'
    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    # خواندن سفارش‌ها
    order_file = f'orders_{shop_id}.json'
    if os.path.exists(order_file):
        with open(order_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        orders = []

    return render_template('dashboard.html', shop=shop, shop_id=shop_id, product_count=len(products), orders=orders)







@app.route('/product/<int:shop_id>/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(shop_id, product_id):
    check_owner(shop_id)

    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        return "⛔ فایل محصول یافت نشد", 404

    if 0 <= product_id < len(products):
        product = products[product_id]

        if request.method == 'POST':
            product['product_name'] = request.form.get('product_name')
            product['price'] = request.form.get('price')
            product['discount'] = request.form.get('discount') if request.form.get('has_discount') else None

            keep_images = []
            for idx, img in enumerate(product['images']):
                if request.form.get(f'remove_image_{idx}') != 'on':
                    keep_images.append(img)

            product['images'] = keep_images

            new_images = request.files.getlist('new_images')
            for image in new_images:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)
                    product['images'].append(filepath)

            products[product_id] = product
            with open(product_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            return redirect(url_for('show_products', shop_id=shop_id))

        return render_template("edit_product.html", product=product, shop_id=shop_id, product_id=product_id)
    else:
        return "⛔ شناسه محصول نامعتبر", 404









@app.route('/product/<int:shop_id>/delete/<int:product_id>')
def delete_product(shop_id, product_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    if 0 <= product_id < len(products):
        products.pop(product_id)
        with open(product_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

    return redirect(url_for('show_products', shop_id=shop_id))






from flask import session

@app.route('/add_to_cart/<int:shop_id>/<int:product_id>', methods=['POST', 'GET'])
def add_to_cart(shop_id, product_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    if 0 <= product_id < len(products):
        product = products[product_id]

        cart = session.get('cart', {})
        shop_cart = cart.get(str(shop_id), [])

        shop_cart.append(product)
        cart[str(shop_id)] = shop_cart
        session['cart'] = cart

        # ✅ ثبت شناسه حجره فعال
        session['current_shop_id'] = shop_id
        session.modified = True

        # ✅ برگشت به فروشگاه همان حجره
        return redirect(url_for('shop_store', shop_id=shop_id))
    else:
        return "⛔️ محصول پیدا نشد", 404





@app.route('/cart')
def cart():
    shop_id = session.get("current_shop_id")

    if shop_id is None:
        return "⛔️ شناسه حجره یافت نشد", 400

    cart = session.get('cart', {}).get(str(shop_id), [])
    total = 0

    for item in cart:
        try:
            price = int(item.get('price', 0))
            discount = int(item.get('discount', 0)) if item.get('discount') else 0
            total += price - discount
        except Exception as e:
            print("❗ خطا در محاسبه قیمت:", e, item)

    print("📦 سبد خرید:", cart)
    print("💰 مجموع قابل پرداخت:", total)

    return render_template('cart.html', cart=cart, total=total, shop_id=shop_id)






def send_sms_faraz(to, message):
    url = "https://rest.farazsms.com/api/SendSMS"
    payload = {
        "username": "09132560530",
        "password": "OWYxYjk5NzktODdhMy00ZDNlLTk4OWMtZmM4OTc0MmE2N2MxZGUxYWU5MzY1MjNlODhmY2FhZDY2MDk4YmMxNmZmNTk=",
        "source": "+9810003894459463",
        "destinations": [to],
        "message": message
    }

    try:
        response = requests.post(url, json=payload)
        print("✅ ارسال پیامک:", response.text)
    except Exception as e:
        print("❌ خطا در ارسال پیامک:", str(e))








def get_shamsi_datetime():
    iran_tz = pytz.timezone('Asia/Tehran')
    now_tehran = datetime.now(iran_tz)
    shamsi = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    return shamsi.strftime('%Y/%m/%d - %H:%M')











from datetime import datetime
import pytz
import jdatetime

def get_shamsi_datetime():
    iran_tz = pytz.timezone('Asia/Tehran')
    now_tehran = datetime.now(iran_tz)
    shamsi = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    return shamsi.strftime('%Y/%m/%d - %H:%M')






from datetime import datetime
import pytz
import requests

@app.route('/checkout/<int:shop_id>', methods=['POST'])
def checkout(shop_id):
    # بارگذاری محصولات از سبد خرید
    cart = session.get('cart', {}).get(str(shop_id), [])
    if not cart:
        return "⛔️ سبد خرید خالی است.", 400

    # دریافت اطلاعات مشتری
    customer_name = request.form.get('name')
    customer_phone = request.form.get('phone')
    address = request.form.get('address')
    notes = request.form.get('notes', '')
    payment_method = request.form.get('payment_method', 'cod')  # در محل یا آنلاین

    # محاسبه مبلغ کل
    total = 0
    for item in cart:
        price = int(item.get('price', 0))
        discount = int(item.get('discount', 0)) if item.get('discount') else 0
        total += price - discount

    # بارگذاری اطلاعات حجره
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            shops = json.load(f)
    else:
        shops = []

    if 0 <= shop_id < len(shops):
        shop = shops[shop_id]
    else:
        return "⛔️ حجره یافت نشد", 404

    # ذخیره سفارش
    order = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "address": address,
        "notes": notes,
        "total": total,
        "items": cart,
        "payment_method": payment_method,
        "datetime": datetime.now(pytz.timezone('Asia/Tehran')).strftime('%Y/%m/%d %H:%M:%S')
    }

    orders_file = f'orders_{shop_id}.json'
    if os.path.exists(orders_file):
        with open(orders_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        orders = []

    orders.append(order)

    with open(orders_file, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

    # 🟢 ارسال پیامک از طریق فراز
    api_key = "OWYxYjk5NzktODdhMy00ZDNlLTk4OWMtZmM4OTc0MmE2N2MxZGUxYWU5MzY1MjNlODhmY2FhZDY2MDk4YmMxNmZmNTk="
    sms_url = "https://api2.farazsms.com/api/SendSMS"
    sender = "5000XXXXXXXX"  # ❗️شماره اختصاصی شما در فراز اس‌ام‌اس

    # پیامک به مشتری
    customer_msg = f"✅ سفارش شما ثبت شد.\nفروشگاه: {shop['shop_name']}\nمبلغ: {total} تومان\nبا تشکر از خرید شما 🌟"
    requests.post(sms_url, json={
        "ApiKey": api_key,
        "Recipient": customer_phone,
        "Sender": sender,
        "Message": customer_msg
    })

    # پیامک به صاحب حجره
    owner_msg = f"📥 سفارش جدید ثبت شد!\nمشتری: {customer_name}\nمبلغ: {total} تومان"
    requests.post(sms_url, json={
        "ApiKey": api_key,
        "Recipient": shop['phone'],
        "Sender": sender,
        "Message": owner_msg
    })

    # پاک‌سازی سبد خرید پس از ثبت سفارش
    session['cart'][str(shop_id)] = []
    session.modified = True

    return render_template("checkout_success.html", shop=shop, order=order)









@app.route('/order/<int:index>')
def order_detail(index):
    if 'shop_id' not in session:
        return redirect(url_for('login'))

    shop_id = session['shop_id']
    order_file = f'orders_{shop_id}.json'

    if os.path.exists(order_file):
        with open(order_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        return "⛔ فایل سفارش یافت نشد", 404

    if 0 <= index < len(orders):
        return render_template('order_detail.html', order=orders[index])
    else:
        return "⛔ سفارش یافت نشد", 404













@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
