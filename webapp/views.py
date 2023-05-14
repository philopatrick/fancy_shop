import requests
from flask import Blueprint, render_template, session, url_for
from models import User, Vendor, Order


def get_login_detail():
   user_id = session.get('user_id')
   role = session.get('role')
   login_bool = False
   user = None
   if role == 'user':
      user = User.query.get(user_id)
      login_bool = True
   elif role == 'vendor':
      user = Vendor.query.get(user_id)
      login_bool = True

   return login_bool, role, user

views_bp = Blueprint('views', __name__)

@views_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@views_bp.route('/', methods=['GET'])
def index():
    login_bool, role, logined = get_login_detail()
    response1 = requests.get('http://localhost:5555/products')
    response2 = requests.get('http://localhost:5555//categories')
    # Parse the JSON response
    products = response1.json()
    categories = response2.json()

    if login_bool:
        return render_template('main.html',user=logined, products=products,  categories=categories)
    else:
        return render_template('main.html', products=products,  categories=categories)
    


@views_bp.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@views_bp.route('/profile', methods=['GET'])
def profile():
    login_bool, role, logined = get_login_detail()
    
    return render_template('profile.html',user=logined)

@views_bp.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    response1 = requests.get(f'http://localhost:5555/products/{product_id}')
    product_data = response1.json()

    response2 = requests.get(f'http://localhost:5555/products/{product_id}/feedback')
    feedback = response2.json()
    
    login_bool, role, logined = get_login_detail()
    return render_template('product_detail.html', product=product_data, feedback=feedback, user=logined)

@views_bp.route('/cart/<int:user_id>', methods=['GET'])
def cart(user_id):
    # response1 = requests.get(f'http://localhost:5555/users/{user_id}/cart')
    # cart = response1.json()
    user = User.query.get(user_id)
    if not user.cart:
        return render_template('cart.html', user=user,)
    cart = user.cart[0]
    #login_bool, role, logined = get_login_detail()
    if not cart:
        return render_template('cart.html', user=user,)

    return render_template('cart.html',cart=cart, user=user,)

@views_bp.route('/checkout/<int:product_id>', methods=['GET'])
def checkoutsingle(product_id):
    response1 = requests.get(f'http://localhost:5555/products/{product_id}')
    product = response1.json()

    login_bool, role, logined = get_login_detail()
    return render_template('check.html',product=product, user=logined)

@views_bp.route('/checkoutcart/<int:user_id>', methods=['GET'])
def checkoutcart(user_id):
    user = User.query.get(user_id)
    cart = user.cart[0]

    login_bool, role, logined = get_login_detail()
    return render_template('check.html',cart=cart, user=logined)

@views_bp.route('/vendor/product/<int:vendor_id>', methods=['GET'])
def vendorproduct(vendor_id):
    response1 = requests.get(f'http://localhost:5555/vendors/{vendor_id}/products')
    response2 = requests.get('http://localhost:5555/categories')
    # Parse the JSON response
    products = response1.json()
    categories = response2.json()
    login_bool, role, logined = get_login_detail()
    return render_template('product.html', products=products, categories=categories, user=logined)

@views_bp.route('/vendor/edit/product/<int:product_id>', methods=['GET'])
def edit_product(product_id):
    response1 = requests.get(f'http://localhost:5555/products/{product_id}')
    product_data = response1.json()
    response2 = requests.get('http://localhost:5555/categories')
    categories = response2.json()

    login_bool, role, logined = get_login_detail()
    return render_template('edit_product.html', product=product_data, categories=categories, user=logined)

@views_bp.route('/orders', methods=['GET'])
def orders():
    login_bool, role, logined = get_login_detail()
    orders = None
    if login_bool:
        if role == 'user':
            orders = Order.get_orders_for_user(logined.id)
            #print(orders)
            return render_template('order.html', user=logined, orders=orders)
        else:
            orders = Order.get_orders_for_vendor(logined.id)
            #print(orders)
            return render_template('order.html', user=logined, orders=orders)