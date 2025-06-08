from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)

# تنظیمات مسیر آپلود عکس
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'hojreh_data.json'


# 📌 صفحه اصلی
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







# 📌 نمایش لیست حجره‌ها
@app.route('/shops')
def show_shops():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    return render_template("shops.html", shops=data)


# 📌 جزئیات هر حجره
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


# 📌 حذف حجره
@app.route('/delete/<int:shop_id>')
def delete_shop(shop_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    if 0 <= shop_id < len(data):
        deleted = data.pop(shop_id)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"🗑️ حجره حذف شد: {deleted['shop_name']}")
        return render_template("delete_success.html", shop_name=deleted['shop_name'])
    else:
        return "⛔ شناسه نامعتبر", 404


# 📌 ویرایش حجره
@app.route('/edit/<int:shop_id>', methods=['GET', 'POST'])
def edit_shop(shop_id):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        return "⛔ فایل داده‌ها پیدا نشد", 404

    if 0 <= shop_id < len(data):
        if request.method == 'POST':
            data[shop_id]['shop_name'] = request.form.get('shop_name')
            data[shop_id]['phone'] = request.form.get('phone')
            data[shop_id]['category'] = request.form.get('category')

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return render_template("edit_success.html", shop=data[shop_id])
        else:
            return render_template("edit.html", shop=data[shop_id], shop_id=shop_id)
    else:
        return "⛔ شناسه حجره نامعتبر است", 404


# 📌 ثبت محصول برای حجره
@app.route('/product/<int:shop_id>', methods=['GET', 'POST'])
def add_product(shop_id):
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


# 📌 نمایش محصولات حجره
@app.route('/products/<int:shop_id>')
def show_products(shop_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    return render_template("show_products.html", products=products, shop_id=shop_id)




@app.route('/product/<int:shop_id>/delete/<int:product_id>')
def delete_product(shop_id, product_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    if 0 <= product_id < len(products):
        deleted = products.pop(product_id)
        with open(product_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"🗑️ محصول حذف شد: {deleted['product_name']}")

    return redirect(url_for('show_products', shop_id=shop_id))








@app.route('/product/<int:shop_id>/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(shop_id, product_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        return "⛔ فایل محصول یافت نشد", 404

    if 0 <= product_id < len(products):
        product = products[product_id]

        if request.method == 'POST':
            # به‌روزرسانی اطلاعات متنی
            product['product_name'] = request.form.get('product_name')
            product['price'] = request.form.get('price')
            product['discount'] = request.form.get('discount') if request.form.get('has_discount') else None

            # حذف عکس‌هایی که تیک خوردن
            keep_images = []
            for idx, img in enumerate(product['images']):
                if request.form.get(f'remove_image_{idx}') != 'on':
                    keep_images.append(img)
                else:
                    print(f"✅ حذف عکس: {img}")
                    # در صورت نیاز: os.remove(img) ← اگه بخوای عکس حذف فیزیکی هم بشه

            product['images'] = keep_images

            # اضافه کردن عکس‌های جدید
            new_images = request.files.getlist('new_images')
            for image in new_images:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)
                    product['images'].append(filepath)

            # ذخیره فایل
            products[product_id] = product
            with open(product_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            return redirect(url_for('show_products', shop_id=shop_id))

        return render_template("edit_product.html", product=product, shop_id=shop_id, product_id=product_id)
    else:
        return "⛔ شناسه محصول نامعتبر", 404





@app.route('/shop/<int:shop_id>/products')
def shop_store(shop_id):
    product_file = f'products_{shop_id}.json'

    if os.path.exists(product_file):
        with open(product_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        products = []

    return render_template("shop_store.html", products=products, shop_id=shop_id)
















# 🔚 اجرای سرور
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
