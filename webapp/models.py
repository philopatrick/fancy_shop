from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash



'''
password = 'secret'
# Generate a hashed password
password_hash = generate_password_hash(password)

# Check if the given password matches the hashed password
is_correct_password = check_password_hash(password_hash, password)
'''

class User(db.Model):
  
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  password_hash = db.Column(db.String(60), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  address = db.Column(db.String(200), nullable=False)
  phone_number = db.Column(db.String(20), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_password(kwargs.get('password_hash'))

  def set_password(self, password):
    """Set the password hash for a given password."""
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    """Check if the given password matches the user's password hash."""
    return check_password_hash(self.password_hash, password)

  # def buy_product(self, product, quantity):
  #   order = Order(user_id=self.id, product_id=product.id, quantity=quantity, price=product.price)
  #   db.session.add(order)
  #   db.session.commit()

  # def like_product(self, product):
  #   like = LikeDislike(user_id=self.id, product_id=product.id, vote_type='like')
  #   db.session.add(like)
  #   db.session.commit()

  # def dislike_product(self, product):
  #   dislike = LikeDislike(user_id=self.id, product_id=product.id, vote_type='dislike')
  #   db.session.add(dislike)
  #   db.session.commit()

  def post_comment(self, product, text):
    comment = Comment(username=self.username, product_id=product.id, text=text)
    db.session.add(comment)
    db.session.commit()

  def serialize(self):
    return {
    'id': self.id,
    'username': self.username,
    'email': self.email,
    'address': self.address,
    'phone_number': self.phone_number,
    'cart': self.cart[0].serialize() if self.cart else None,
    'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }


class Vendor(db.Model):
  __tablename__ = 'vendors'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  password_hash = db.Column(db.String(60), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  address = db.Column(db.String(200), nullable=False)
  phone_number = db.Column(db.String(20), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  products = db.relationship('Product', backref='vendor', lazy=True)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_password(kwargs.get('password_hash'))

  def set_password(self, password):
    """Set the password hash for a given password."""
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    """Check if the given password matches the user's password hash."""
    return check_password_hash(self.password_hash, password)
  
  def add_product(self, product):
    product.vendor_id = self.id
    db.session.add(product)
    db.session.commit()

  def serialize(self):
    return {
      'id': self.id,
      'username': self.username,
      'email': self.email,
      'address': self.address,
      'phone_number': self.phone_number,
      'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

class Category(db.Model):
  __tablename__ = 'categories'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), unique=True, nullable=False)

  products = db.relationship('Product', backref='category', lazy=True)

  def serialize(self):
    return {
      'id': self.id,
      'name': self.name
    }

class Product(db.Model):
  __tablename__ = 'products'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text, nullable=False)
  price = db.Column(db.Float, nullable=False)
  image = db.Column(db.String(255), nullable=False)
  vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  orders = db.relationship('Order', backref='product', lazy=True)
  comments = db.relationship('Comment', backref='product', lazy=True)
  likes_dislikes = db.relationship('LikeDislike', backref='product', lazy=True)

  def get_likes(self):
    return len([vote for vote in self.likes_dislikes if vote.vote_type == 'like'])

  def get_dislikes(self):
    return len([vote for vote in self.likes_dislikes if vote.vote_type == 'dislike'])
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'price': self.price,
      'image': self.image,
      'vendor_id': self.vendor_id,
      'category_id': self.category_id,
      'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
      'likes': self.get_likes(),
      'dislikes': self.get_dislikes()
      }

class Comment(db.Model):
  __tablename__ = 'comments'
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.Text, nullable=False)
  username = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def serialize(self):
    return {
    'id': self.id,
    'text': self.text,
    'username': self.username,
    'product_id': self.product_id,
    'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

class Order(db.Model):
  __tablename__ = 'orders'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
  quantity = db.Column(db.Integer, nullable=False)
  price = db.Column(db.Float, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  shipped_at = db.Column(db.DateTime)
  received_at = db.Column(db.DateTime)
  message = db.Column(db.Text)
  
  user = db.relationship('User', backref='orders')
  vendor = db.relationship('Vendor', backref='orders')
  #product = db.relationship('Product', backref='orders')

  def serialize(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'vendor_id': self.vendor_id,
      'product_id': self.product_id,
      'quantity': self.quantity,
      'price': self.price,
      'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
      'shipped_at': self.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if self.shipped_at else None,
      'received_at': self.received_at.strftime('%Y-%m-%d %H:%M:%S') if self.received_at else None,
      'message': self.message
    }

  def mark_as_shipped(self, message):
    """Mark the order as shipped by the vendor."""
    if not self.shipped_at:
      self.shipped_at = datetime.utcnow()
      self.message = message
      db.session.commit()

  def mark_as_received(self):
    """Mark the order as received by the user."""
    if not self.received_at:
      self.received_at = datetime.utcnow()
      db.session.commit()

  @staticmethod
  def get_orders_for_user(user_id):
    """Get all orders for a given user ID."""
    return Order.query.filter_by(user_id=user_id).all()

  @staticmethod
  def get_orders_for_vendor(vendor_id):
    """Get all orders for a given vendor ID."""
    return Order.query.filter_by(vendor_id=vendor_id).all()
  
class LikeDislike(db.Model):
  __tablename__ = 'likes_dislikes'
  user_id = db.Column(db.Integer,db.ForeignKey('users.id'), primary_key=True)
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
  vote_type = db.Column(db.String(10), nullable=False) # either 'like' or 'dislike'

  def serialize(self):
    return {
    'user_id': self.user_id,
    'product_id': self.product_id,
    'vote_type': self.vote_type
    }
  


class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False,)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='cart')
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [item.serialize() for item in self.items]
        }

    def add_item(self, product, quantity):
        """Add a new item to the cart."""
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product.id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=self.id, product_id=product.id, quantity=quantity, price=product.price)
            db.session.add(item)
        db.session.commit()

    def remove_item(self, product):
        """Remove an item from the cart."""
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product.id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            
    def remove_all(self):
        """Remove all items from the cart."""
        for item in self.items:
            db.session.delete(item)
            db.session.commit()

    def update_item_quantity(self, product, quantity):
        """Update the quantity of an item in the cart."""
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product.id).first()
        if item:
            item.quantity = quantity
            db.session.commit()

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.price * item.quantity for item in self.items)


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    cart = db.relationship('Cart', backref='items')
    product = db.relationship('Product')

    def serialize(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }