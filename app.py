from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    shop_name = request.form.get('shop_name')
    phone = request.form.get('phone')
    category = request.form.get('category')
    
    print(f"حجره جدید ثبت شد: {shop_name}, {phone}, {category}")
    
    return f"✅ حجره با نام {shop_name} ثبت شد!"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
