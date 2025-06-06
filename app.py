from flask import Flask, request, render_template
import os
import json

app = Flask(__name__)

DATA_FILE = 'hojreh_data.json'

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    shop_name = request.form.get('shop_name')
    phone = request.form.get('phone')
    category = request.form.get('category')

    new_shop = {
        "shop_name": shop_name,
        "phone": phone,
        "category": category
    }

    # اگر فایل وجود داره، بخون
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    # اضافه کردن حجره جدید
    data.append(new_shop)

    # ذخیره در فایل
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return f"✅ حجره با نام {shop_name} ثبت شد!"



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








if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)










