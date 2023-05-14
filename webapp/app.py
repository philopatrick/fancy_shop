from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, jsonify, request, session, url_for
from models import db, User, Vendor, Category, Product, LikeDislike, Comment, Order, Cart
from werkzeug.utils import secure_filename

from flask_migrate import Migrate
from views import views_bp







app = Flask(__name__)
app.register_blueprint(views_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
app.secret_key="random key"
# Set the upload folder location
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/upload')
migrate = Migrate(app, db)
db.init_app(app)


def get_login_detail():
   user_id = session.get('user_id')
   role = session.get('role')
   login_bool = False
      
   if role == 'user':
      username = User.query.get(user_id).username
      login_bool = True
   elif role == 'vendor':
      username = Vendor.query.get(user_id).username
      login_bool = True

   return login_bool, user_id, role, username





"""
User register and User login
"""
@app.route('/register', methods=['POST'])
def register():
  username = request.json.get('username')
  password = request.json.get('password')
  email = request.json.get('email')
  address = request.json.get('address')
  phone_number = request.json.get('phone_number')
  role = request.json.get('role')
  
  if role == 'user':
     
    # Check if the username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    # Create a new user object
    user = User(username=username, password_hash=password, email=email, address=address, phone_number=phone_number, created_at=datetime.utcnow())

    # Add the user to the database
    db.session.add(user)
    db.session.commit()

    # Return the serialized user object
    return jsonify(user.serialize())
  
  elif role == 'vendor':
     # Check if the username or email already exists
    if Vendor.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if Vendor.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    # Create a new user object
    vendor = Vendor(username=username, password_hash=password, email=email, address=address, phone_number=phone_number, created_at=datetime.utcnow())

    # Add the user to the database
    db.session.add(vendor)
    db.session.commit()

    # Return the serialized user object
    return jsonify(vendor.serialize())


@app.route('/login', methods=['POST'])
def login():
  email = request.json.get('email')
  password = request.json.get('password')

  role = request.json.get('role')
  
  print(email,password,role)
  # Check if the user exists in the database
  if role == 'user':
    user = User.query.filter_by(email=email).first()
  elif role == 'vendor':
    user = Vendor.query.filter_by(email=email).first()
  else:
    return jsonify({'error': 'Invalid role'}), 400

  if not user:
    return jsonify({'error': 'Invalid email or password'}), 401

  # Check if the password is correct
  if not user.check_password(password):
    return jsonify({'error': 'Invalid email or password'}), 401

  # Save the user ID and role in the session
  session['user_id'] = user.id
  session['role'] = role
  # Return the serialized user object
  return jsonify(user.serialize())


@app.route('/logout')
def logout():
  # Remove the user ID and role from the session
  session.pop('user_id', None)
  session.pop('role', None)
  
  return redirect(url_for('views.index'))
  #return jsonify({'message': 'Logged out successfully'})

@app.route('/updateprofile/', methods=['PUT'])
def update_profile():
  

  login_bool, user_id, role, username = get_login_detail()
  user_id = session['user_id']
  role = session['role']

  if role=='user':
    user = User.query.get(user_id)
  elif role=='vendor':
    user = Vendor.query.get(user_id)

  if not user:
    return jsonify({'error': 'User not found'}), 404
  
   # Update the user with the new data
  name = request.json.get('name')
  email = request.json.get('email')
  password = request.json.get('password')
  address = request.json.get('address')
  phone_number = request.json.get('phone_number')

  if name:
    user.username = name

  if email:
    user.email = email

  if password:
    user.set_password(password)

  if address:
    user.address = address

  if phone_number:
    user.phone_number = phone_number

  # Commit the changes to the database
  db.session.commit()

  # Return the serialized user object
  return jsonify(user.serialize())

@app.route('/getprofile/', methods=['GET'])
def get_profile():
  

  login_bool, user_id, role, username = get_login_detail()
  user_id = session['user_id']
  role = session['role']
     
  if role=='user':
    user = User.query.get(user_id)
  elif role=='vendor':
    user = Vendor.query.get(user_id)

  return jsonify(user.serialize())

'''
Get and Add categories
'''

@app.route('/categories', methods=['GET'])
def get_categories():
  # Retrieve all categories from the database
  categories = Category.query.all()

  # Serialize the categories into a list
  serialized_categories = [category.serialize() for category in categories]

  return jsonify(serialized_categories)


@app.route('/categories', methods=['POST'])
def add_category():
  name = request.form.get('name')

  # Check if the category already exists
  if Category.query.filter_by(name=name).first():
    return jsonify({'error': 'Category already exists'}), 400

  # Create a new category object
  category = Category(name=name)

  # Add the category to the database
  db.session.add(category)
  db.session.commit()
  
  user_id = session.get('user_id')
  # Return the serialized category object with 201 status code
  return redirect(url_for('views.vendorproduct', vendor_id=user_id))

'''
Add product, get all products, get products under categories, get products under vendor, get product under id, edit product under id
'''
@app.route('/products', methods=['POST'])
def add_product():
  # Retrieve data from the request json
  name = request.form.get('name')
  description = request.form.get('description')
  price = request.form.get('price')
  image_file = request.files['image']
  
  # Check if the user is a vendor
  if session.get('role') != 'vendor':
    return redirect(url_for('login'))

  vendor_id = session.get('user_id')

  # Check if the vendor exists
  vendor = Vendor.query.get(vendor_id)

  if not vendor:
    return jsonify({'error': 'Vendor not found'}), 404

  category_id = request.form.get('category_id')

  # Check if the category exists
  category = Category.query.get(category_id)

  if not category:
    return jsonify({'error': 'Category not found'}), 404

  # Save the image file to disk

  filename = secure_filename(image_file.filename)
  image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

  # Create a new product object
  product = Product(name=name, description=description, price=price, image=filename, vendor_id=vendor_id, category_id=category_id, created_at=datetime.utcnow())

  # Add the product to the database
  db.session.add(product)
  db.session.commit()

  user_id = session.get('user_id')
  # Return the serialized category object with 201 status code
  return redirect(url_for('views.vendorproduct', vendor_id=user_id))


@app.route('/products', methods=['GET'])
def get_all_products():
  # Retrieve all products from the database
  products = Product.query.all()

  # Serialize the products into a list
  serialized_products = [product.serialize() for product in products]

  return jsonify(serialized_products)


@app.route('/categories/<int:category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
  # Retrieve the products for the specified category from the database
  products = Product.query.filter_by(category_id=category_id).all()

  # Return the serialized list of product objects
  return jsonify([product.serialize() for product in products])

@app.route('/vendors/<int:vendor_id>/products', methods=['GET'])
def get_products_by_vendor(vendor_id):
  # Retrieve the products for the specified vendor from the database
  products = Product.query.filter_by(vendor_id=vendor_id).all()

  # Return the serialized list of product objects
  return jsonify([product.serialize() for product in products])


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
  # Retrieve the product from the database
  product = Product.query.get(product_id)

  if not product:
    return jsonify({'error': 'Product not found'}), 404

  # Return the serialized product object
  return jsonify(product.serialize())

@app.route('/products/<int:product_id>', methods=['POST'])
def edit_product(product_id):
  # Retrieve the product from the database

  # Check if the user is a vendor
  if session.get('role') != 'vendor':
    return redirect(url_for('login'))

  vendor_id = session.get('user_id')

  # Check if the vendor exists
  vendor = Vendor.query.get(vendor_id)

  if not vendor:
    return jsonify({'error': 'Vendor not found'}), 404
  
  product = Product.query.get(product_id)

  if not product:
    return jsonify({'error': 'Product not found'}), 404

  # Update the product with the new data
  name = request.form.get('name')
  description = request.form.get('description')
  price = request.form.get('price')
  category_id = request.form.get('category_id')
  image_file = request.files.get('image')

  if name:
    product.name = name

  if description:
    product.description = description

  if image_file:
    filename = secure_filename(image_file.filename)
    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    product.image = filename

  if price:
     product.price = price
    
  if category_id:
     product.category_id = category_id
  # Commit the changes to the database
  db.session.commit()

  user_id = session.get('user_id')
  # Return the serialized category object with 201 status code
  return redirect(url_for('views.vendorproduct', vendor_id=user_id))


"""
User like or dislike a product
"""

@app.route('/users/like/<int:product_id>', methods=['POST'])
def like_product(product_id):
  # Retrieve the user and product from the database
  login_bool, user_id, role, username = get_login_detail()
  if not login_bool:
     return redirect(url_for(login))
  user = User.query.get(user_id)
  product = Product.query.get(product_id)

  if not user or not product:
    return jsonify({'error': 'User or product not found'}), 404

  # Add the user's like to the product's likes_dislikes relationship
  like_dislike = LikeDislike.query.filter_by(user_id=user.id, product_id=product.id).first()
  if not like_dislike:
      like_dislike = LikeDislike(user_id=user.id, product_id=product.id)
      db.session.add(like_dislike)
  like_dislike.vote_type = 'like'

  # Remove the user's dislike from the product's likes_dislikes relationship if present
  dislike_dislike = LikeDislike.query.filter_by(user_id=user.id, product_id=product.id).first()
  if dislike_dislike and dislike_dislike.vote_type=='dislike':
      db.session.delete(dislike_dislike)

  # Commit the changes to the database
  db.session.commit()

  response_form = {
     'success': 'like success',
     'count': product.get_likes()
  }
  # Return the serialized user object
  return jsonify(response_form)

@app.route('/users/dislike/<int:product_id>', methods=['POST'])
def dislike_product(product_id):
  # Retrieve the user and product from the database
  login_bool, user_id, role, username = get_login_detail()
  if not login_bool:
     return redirect(url_for(login))
  user = User.query.get(user_id)
  product = Product.query.get(product_id)

  if not user or not product:
    return jsonify({'error': 'User or product not found'}), 404

  # Add the user's dislike to the product's likes_dislikes relationship
  like_dislike = LikeDislike.query.filter_by(user_id=user.id, product_id=product.id).first()
  if not like_dislike:
      like_dislike = LikeDislike(user_id=user.id, product_id=product.id)
      db.session.add(like_dislike)
  like_dislike.vote_type = 'dislike'

  # Remove the user's like from the product's likes_dislikes relationship if present
  like_dislike = LikeDislike.query.filter_by(user_id=user.id, product_id=product.id).first()
  if like_dislike and like_dislike.vote_type=='like':
      db.session.delete(like_dislike)

  # Commit the changes to the database
  db.session.commit()

  response_form = {
     'success': 'like success',
     'count': product.get_dislikes()
  }
  # Return the serialized user object
  return jsonify(response_form)



@app.route('/users/products/<int:product_id>/comments', methods=['POST'])
def post_comment(product_id):
  # Retrieve the user and product from the database
  login_bool, user_id, role, username = get_login_detail()
  if not login_bool:
     return redirect(url_for(login))
  user = User.query.get(user_id)
  product = Product.query.get(product_id)

  if not user or not product:
    return jsonify({'error': 'User or product not found'}), 404

  # Get the comment text from the request json
  text = request.json.get('text')

  if not text:
    return jsonify({'error': 'Comment text is missing'}), 400

  # Create a new comment and add it to the product's comments list
  user.post_comment(product,text)

  response_form = {
     'success': 'comment success',
     
  }
  # Return the serialized product object
  return jsonify(response_form)


@app.route('/products/<int:product_id>/feedback', methods=['GET'])
def get_product_feedback(product_id):
  # Retrieve the product from the database
  product = Product.query.get(product_id)

  if not product:
    return jsonify({'error': 'Product not found'}), 404

  # Get the number of likes, dislikes, and comments for the product
  num_likes = LikeDislike.query.filter_by(product_id=product.id, vote_type='like').count()
  num_dislikes = LikeDislike.query.filter_by(product_id=product.id, vote_type='dislike').count()
  # Get all comments for the product and serialize them with author information
  comments = Comment.query.filter_by(product_id=product.id).all()
  serialized_comments = []
  for comment in comments:
    serialized_comment = {
      'username': comment.username,
      'text': comment.text,
      'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    serialized_comments.append(serialized_comment)
  # Return the feedback data as a JSON object
  feedback = {
    'likes': num_likes,
    'dislikes': num_dislikes,
    'comments': serialized_comments
  }

  return jsonify(feedback)


"""

Order logic
"""

@app.route('/products/<int:product_id>/purchase', methods=['POST'])
def purchase_product(product_id):
    """Endpoint to allow a user to purchase a product."""
    product = Product.query.get_or_404(product_id)
    vendor = Vendor.query.get_or_404(product.vendor_id)


    user_id = session.get('user_id')

    current_user = User.query.get(user_id)

    if not current_user:
     return redirect(url_for('login'))


    quantity = request.form.get('quantity')
    quantity = int(quantity)
    if not quantity or quantity <= 0:
        return jsonify({'error': 'Invalid quantity.'}), 400

    order = Order(
        user_id=current_user.id,
        vendor_id=vendor.id,
        product_id=product.id,
        quantity=quantity,
        price=product.price * int(quantity)
    )
    db.session.add(order)
    db.session.commit()

    return redirect(url_for('views.orders'))
    # return jsonify({'order': order.serialize()})


@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_orders_for_user(user_id):
    orders = Order.get_orders_for_user(user_id)
    return jsonify([order.serialize() for order in orders])


@app.route('/vendors/<int:vendor_id>/orders', methods=['GET'])
def get_orders_for_vendor(vendor_id):
    orders = Order.get_orders_for_vendor(vendor_id)
    return jsonify([order.serialize() for order in orders])



@app.route('/vendors/orders/<int:order_id>/shipped', methods=['POST','GET'])
def mark_order_as_shipped(order_id):
    order = Order.query.get(order_id)
    if request.method == 'POST':
      if not order:
          return jsonify({'error': 'Order not found'}), 404
      message = request.form.get('message')
      if not message:
          return jsonify({'error': 'Message is required'}), 400
      order.mark_as_shipped(message)
      return redirect(url_for('views.orders'))
      # return jsonify({'message': 'Order marked as shipped'})
    return render_template('mark.html', order=order)


@app.route('/users/orders/<int:order_id>/received', methods=['POST'])
def mark_order_as_received(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    order.mark_as_received()
    return jsonify({'message': 'Order marked as received'})



# Get the contents of the user's cart
@app.route('/users/<int:user_id>/cart', methods=['GET'])
def get_cart(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.cart:
        return jsonify({'message': 'Cart is empty'})
    return jsonify(user.cart[0].serialize())

# Add a new item to the user's cart
@app.route('/users/cart/items/', methods=['POST'])
def add_to_cart():
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    quantity = int(quantity)
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than zero'}), 400
    if not user.cart:
        cart = Cart(user_id=user.id)
        #user.cart = cart
        db.session.add(cart)
        db.session.commit()
    user.cart[0].add_item(product, quantity)
    return jsonify({'message': 'Item added to cart'})

# Remove an item from the user's cart
@app.route('/users/<int:user_id>/cart/items/<int:product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.cart:
        return jsonify({'error': 'Cart is empty'}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    user.cart[0].remove_item(product)
    return jsonify({'message': 'Item removed from cart'})

# Update the quantity of an item in the user's cart
@app.route('/users/<int:user_id>/cart/items/<int:product_id>', methods=['PUT'])
def update_cart_item_quantity(user_id, product_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.cart:
        return jsonify({'error': 'Cart is empty'}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    quantity = int(request.json.get('quantity'))

    if quantity is None or quantity <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    user.cart[0].update_item_quantity(product, quantity)
    return jsonify({'message': 'Item quantity updated'})

# Get the total price of the user's cart
@app.route('/users/<int:user_id>/cart/total', methods=['GET'])
def get_cart_total(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.cart:
        return jsonify({'message': 'Cart is empty'})
    total_price = user.cart[0].get_total_price()
    return jsonify({'total_price': total_price})


@app.route('/users/<int:user_id>/cart/buy', methods=['POST'])
def buy_cart(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.cart:
        return jsonify({'error': 'Cart is empty'}), 400
    total_price = user.cart[0].get_total_price()
    if total_price == 0:
        return jsonify({'error': 'Cart is empty'}), 400
    
    for item in user.cart[0].items:
        order_item = Order(
        user_id=user.id,
        vendor_id=Product.query.get(item.product_id).id,
        product_id=item.product.id,
        quantity=item.quantity,
        price=item.price
    )
        db.session.add(order_item)
    user.cart[0].remove_all()
    db.session.delete(user.cart[0])
    db.session.commit()
    return redirect(url_for('views.orders'))
    #return jsonify({'message': 'Order created'})




if __name__=='__main__':
    
    app.run(debug=True,port=5555)