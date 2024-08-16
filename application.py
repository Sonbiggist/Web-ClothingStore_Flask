import sqlite3
import os
from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
app = Flask(__name__)

# Cấu hình phiên lam việc
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
Session(app)

# Tạo kết nối dtb
db = SQL ( "sqlite:///data.db" )
db.row_factory = sqlite3.Row
@app.route("/")
def index():
    shirts = db.execute("SELECT * FROM shirts ORDER BY onSalePrice")
    shirtsLen = len(shirts)
    # Khởi tạo các biến
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = db.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
        shirtsLen = len(shirts)
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)



@app.route("/buy/")
def buy():
    # Tạo biến mua hàng
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Lấy id của áo đã chọn
        id = int(request.args.get('id'))
        # Lấy thông tin của áo đã chọn từ dtb
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        # Lấy giá trị từ bản ghi áo đã chọn
        # Kiểm tra xem áo có đang giảm giá không để xác định giá
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        samplename = goods[0]["samplename"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Thêm áo đã chọn vào giỏ hàng
        db.execute("INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)", id=id, qty=qty, samplename=samplename, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
        shopLen = len(shoppingCart)
        # Tính lại giỏ hàng
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Quay lại trang giỏ hàng
        shirts = db.execute("SELECT * FROM shirts ORDER BY samplename ASC")
        shirtsLen = len(shirts)
        # Render trang giỏ hàng
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/update/")
def update():
    # Khởi tạo biến mua hàng
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Lấy id của áo đã chọn
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id", id=id)
        # Lấy thông tin của áo đã chọn từ dtb
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        # Lấy giá trị từ bản ghi áo đã chọn
        # Kiểm tra xem áo có đang giảm giá không để xác định giá
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        samplename = goods[0]["samplename"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Thêm áo đã chọn vào giỏ hàng
        db.execute("INSERT INTO cart (id, qty, samplename, image, price, subTotal) VALUES (:id, :qty, :samplename, :image, :price, :subTotal)", id=id, qty=qty, samplename=samplename, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
        shopLen = len(shoppingCart)
        # Tính lại giỏ hàng
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Quay lại trang giỏ hàng
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('typeClothes'):
        query = request.args.get('typeClothes')
        shirts = db.execute("SELECT * FROM shirts WHERE typeClothes = :query ORDER BY samplename ASC", query=query )
    if request.args.get('sale'):
        query = request.args.get('sale')
        shirts = db.execute("SELECT * FROM shirts WHERE onSale = :query ORDER BY samplename ASC", query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shirts = db.execute("SELECT * FROM shirts WHERE id = :query ORDER BY samplename ASC", query=query)
    if request.args.get('kind'):
        query = request.args.get('kind')
        shirts = db.execute("SELECT * FROM shirts WHERE kind = :query ORDER BY samplename ASC", query=query)
    if request.args.get('price'):
        query = request.args.get('price')
        shirts = db.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
    shirtsLen = len(shirts)
    # Tạo biến mua hàng
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Lấy thông tin giỏ hàng
        shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Quay lại trang chính
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    # Quay lại trang chính
    return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from cart")
    # Cập nhật thông tin mua hàng vào dtb
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, samplename, image, quantity) VALUES(:uid, :id, :samplename, :image, :quantity)", uid=session["uid"], id=item["id"], samplename=item["samplename"], image=item["image"], quantity=item["qty"] )
    # Xóa thông tin mua hàng từ giỏ hàng
    db.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Quay lại trang chính
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    # Lấy id của áo đã chọn
    out = int(request.args.get("id"))
    # Xóa áo đã chọn khỏi giỏ hàng
    db.execute("DELETE from cart WHERE id=:id", id=out)
    # Khởi tạo biến mua hàng
    totItems, total, display = 0, 0, 0
    # Lấy thông tin giỏ hàng
    shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Render trang giỏ hàng
    display = 1
    # Quay lại trang giỏ hàng
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # render traang đăng ký
    return render_template("new.html")

@app.route("/logged/", methods=["POST"])
def logged():
    # Lấy thông tin từ form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    
    # If username or password is empty, return the login page
    if user == "" or pwd == "":
        return render_template("login.html")
    
    # Tìm thông tin người dùng trong dtb
    query = "SELECT * FROM users WHERE username = :user AND password = :pwd"
    rows = db.execute(query, user=user, pwd=pwd)

    # Kiểm tra xem người dùng có phải là admin không
    is_admin = user == "admin" and pwd == "12345678"

    # Nêu người dùng là admin, lưu thông tin vào phiên làm việc
    if len(rows) == 1 or is_admin:
        session['user'] = user
        session['time'] = datetime.now()
        session['uid'] = rows[0]["id"] if len(rows) == 1 else None

    # Nếu người dùng là admin, chuyển hướng đến trang admin
    if 'user' in session:
        return redirect("/") if not is_admin else redirect("/ADMIN")

    # Nếu thông tin không chính xác, thông báo lỗi
    return render_template("login.html", msg="Wrong username or password.")



@app.route("/history/")
def history():
    # Khởi tạo biến mua hàng
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Lấy thông tin giỏ hàng
    myShirts = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShirtsLen = len(myShirts)
    # Tính lại giỏ hàng
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)


@app.route("/logout/")
def logout():
    # Xóa thông tin người dùng
    db.execute("DELETE from cart")
    # Xóa thông tin phiên làm việc
    session.clear()
    # Quay lại trang chính
    return redirect("/")


@app.route("/register/", methods=["POST"] )
def registration():
    # Lấy thông tin từ form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    # Nếu thông tin không hợp lệ, thông báo lỗi
    rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = username )
    # Nếu tên người dùng đã tồn tại, thông báo lỗi
    if len( rows ) > 0:
        return render_template ( "new.html", msg="Username already exists!" )
    # Nếu là người dùng mới, thêm thông tin vào dtb
    new = db.execute ( "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                    username=username, password=password, fname=fname, lname=lname, email=email )
    # Render trang đăng nhập
    return render_template ( "login.html" )


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Khởi tạo biến mua hàng
        totItems, total, display = 0, 0, 0
        # Lấy thông tin giỏ hàng
        shoppingCart = db.execute("SELECT samplename, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY samplename")
        # Tính lại giỏ hàng
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render trang giỏ hàng
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_last_shirt_id():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(id) FROM shirts')
    last_id = cursor.fetchone()[0]
    conn.close()
    return last_id


def generate_next_id():
    last_id = get_last_shirt_id()
    return last_id + 1 if last_id is not None else 1


def generate_samplename(type_clothes):
    last_id = get_last_shirt_id()
    return f'SAMPLE{type_clothes.upper()}{last_id + 1}'


def add_shirt_to_database(samplename, image_filename, price, on_sale, on_sale_price, kind, type_clothes):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO shirts (samplename, image, price, onSale, onSalePrice, kind, typeClothes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (samplename, image_filename, price, on_sale, on_sale_price, kind, type_clothes))

    conn.commit()
    conn.close()

def check_admin_credentials(username):
    return username == 'admin'
@app.route('/ADMIN', methods=['GET', 'POST'])
def admin():
    if session['user'] != 'admin':
            return redirect("/")
    if request.method == 'POST':
        # Tạo id mới
        next_id = generate_next_id()

        # Lấy thông tin từ form
        kind = request.form['kind']
        type_clothes = request.form['typeClothes']
        samplename = generate_samplename(type_clothes)

        # Lưu file ảnh
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Lưu thông tin áo vào dtb
                price = float(request.form['price'])
                on_sale = 1 if 'onSale' in request.form else 0
                on_sale_price = float(request.form['onSalePrice'])

                add_shirt_to_database(samplename, filename, price, on_sale, on_sale_price, kind, type_clothes)
            else:
                # Thông báo lỗi nếu file không hợp lệ
                print('Invalid file type or no file selected')

    return render_template('admin.html')
