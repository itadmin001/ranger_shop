from werkzeug.security import generate_password_hash #allows us to generate a hashed password
from flask_sqlalchemy import SQLAlchemy #allows our database to read our classes/objects as tables/rows 
from flask_login import UserMixin, LoginManager #allows us to load a current logged in user
from datetime import datetime
import uuid #generate a unique id (basically the same serializing last week)
from flask_marshmallow import Marshmallow 

#internal import
from .helpers import get_image



db = SQLAlchemy() #instantiate our database
login_manager = LoginManager() #instantiate our login manager
ma = Marshmallow() #instantiating our Marshmallow class 



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #this queries our database & brings back the user with the same id



class User(db.Model, UserMixin):
    #think of this part as the CREATE TABLE 'User' 
    user_id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    #add the relationship here 

    #think of our __init__() as our INSERT INTO 
    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id() #method to create a unique id
        self.first_name = first_name
        self.last_name = last_name 
        self.username = username
        self.email = email
        self.password = self.set_password(password) #method to hash our password for security 


    def set_id(self):
        return str(uuid.uuid4())
    

    def get_id(self):
        return str(self.user_id)
    

    def set_password(self, password):
        return generate_password_hash(password)
    

    def __repr__(self):
        return f"<USER: {self.username}"
    

class Product(db.Model):
    prod_id = db.Column(db.String, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    image = db.Column(db.String, nullable = False)
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    prodord = db.relationship('ProdOrder', backref = 'product', lazy=True)
    #user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable = False) #if we wanted to make a foreign key relationship


    def __init__(self, name, price, quantity, image = "", description = ""):
        self.prod_id = self.set_id()
        self.name = name
        self.price = price
        self.quantity = quantity
        self.image = self.set_image(image, name)
        self.description = description

    def set_id(self):
        return str(uuid.uuid4()) #create unique ID 
    

    def set_image(self, image, name):
        if not image: #aka image is not present
            image = get_image(name) #adding get_image function which makes an external 3rd party API callh
            print("api image", image)

        return image
    
    def decrement_quantity(self, quantity):

        self.quantity -= int(quantity)
        return self.quantity #all methods need to return otherwise the object attribute doesnt get updated
    
    def increment_quantity(self, quantity):

        self.quantity += int(quantity)
        return self.quantity
    

    def __repr__(self):
        return f"<PRODUCT: {self.name}>"



class Customer(db.Model):
    __tablename__ = 'customer'
    cust_id = db.Column(db.String, primary_key = True)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())
    prodord  = db.relationship('ProdOrder', backref = 'customer', lazy = True) #backref is just how are these related, lazy means a Customer can exist without the ProdOrder table


    def __init__(self, cust_id):
        self.cust_id = cust_id #we are getting their id from the front end 



#Many to Many relationship with Products, Customers & Orders
#So we need a join table

class ProdOrder(db.Model):
    prodorder_id = db.Column(db.String, primary_key = True)
    prod_id = db.Column(db.String, db.ForeignKey('product.prod_id'), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    order_id = db.Column(db.String,  db.ForeignKey('order.order_id'), nullable = False)
    cust_id = db.Column(db.String, db.ForeignKey('customer.cust_id'), nullable = False)


    def __init__(self, prod_id, quantity, price, order_id, cust_id):
        self.prodorder_id = self.set_id()
        self.prod_id = prod_id
        self.quantity = quantity
        self.price = self.set_price(price, quantity)
        self.order_id = order_id
        self.cust_id = cust_id 


    def set_id(self):
        return str(uuid.uuid4())
    


    def set_price(self, price, quantity):

        quantity = int(quantity)
        price = int(price)

        self.price = quantity * price
        return self.price 
    

    def update_quantity(self, quantity): #method used for when customers update their order quantity of a specific product 

        self.quantity = int(quantity)
        return self.quantity
    


class Order(db.Model):
    order_id = db.Column(db.String, primary_key = True)
    order_total = db.Column(db.Numeric(precision = 10, scale = 2), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())
    prodorder = db.relationship('ProdOrder', backref = 'order', lazy = True)


    def __init__(self):
        self.order_id = self.set_id()
        self.order_total = 0.00


    def set_id(self):
        return str(uuid.uuid4())
    

    #for every product's total price in prodorder table add to our order's total price 
    def increment_order_total(self, price):

        self.order_total = float(self.order_total)
        self.order_total += float(price)

        return self.order_total
    
    def decrement_order_total(self, price):

        self.order_total = float(self.order_total)
        self.order_total -= float(price)


        return self.order_total 
    
    def __repr__(self):

        return f"<ORDER: {self.order_id}>"
    

#Because we are building a RESTful API this week (Representational State Transfer) 
#json rules that world. JavaScript Object Notation aka dictionaries 


#Build our Schema
#How your object looks when being passed from server to server 
#These will look like dictionaries 

class ProductSchema(ma.Schema):
    class Meta: 
        fields = ['prod_id', 'name', 'image', 'description', 'price', 'quantity'] 



product_schema = ProductSchema() #this is for passing 1 singular product 
products_schema = ProductSchema(many = True) #this for passing multiple products, list of dictionaries 
    

    