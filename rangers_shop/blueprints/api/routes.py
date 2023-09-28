from flask import Blueprint, request, jsonify 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 

#internal imports 
from rangers_shop.models import Customer, Product, ProdOrder, Order, db, product_schema, products_schema 



#instantiate our blueprint
api = Blueprint('api', __name__, url_prefix = '/api') #all of our endpoints need to be prefixed with /api


@api.route('/token', methods = ['GET', 'POST'])
def token():

    data = request.json

    if data:
        client_id = data['client_id'] #looking for the key of client_id on the dictionary passed to us
        access_token = create_access_token(identity=client_id) 
        return {
            'status' : 200,
            'access_token' : access_token 
        }
    
    else:
        return {
            'status': 400,
            'message': 'Missing Client Id. Try Again'
        }
    
# create read data for shop
@api.route('/shop')
@jwt_required()
def get_shop():
    shop=Product.query.all() #list of objects, we can't send a list of objects through api calls 

    respose=products_schema.dump(shop) #takes our list of objects and turns it into a list of dictionaries 
    return jsonify(respose) #jsonify essentially stringifies the list to send to our frontend 


@api.route('/order/<cust_id>')
@jwt_required()
def get_order(cust_id):


    #We need to grab all the order_ids associated with the customer
    #Grab all the products on that particular order 

    prodorder = ProdOrder.query.filter(ProdOrder.cust_id == cust_id).all()

    data=[]
    print(data)

    #need to traverse to grab all products from each order
    for order in prodorder:
        product=Product.query.filter(Product.prod_id == order.prod_id).first()

        prod_data = product_schema.dump(product) #change this from object to a dict

        prod_data['quantity'] = order.quantity #coming from the prodorder table
        prod_data['order_id'] = order.order_id #want to associate this product with a specific user
        prod_data['id'] = order.prod_id #need to make products usinqe even if they oar the same product

        data.append(prod_data)
    return jsonify(data)


#create our CREATE data request for orders, usually associated with 'POST'
@api.route('/order/create/<cust_id>', methods=['POST'])
@jwt_required()
def create_order(cust_id):

    data = request.json

    customer_order=data['order'] #list of product dicts

    customer = Customer.query.filter(Customer.cust_id == cust_id).first()
    if not customer:
        customer = Customer(cust_id)
        db.session.add(customer)

    order = Order()
    db.session.add(order)
    for product in customer_order:

        prodorder = ProdOrder(product['prod_id'],product['quantity'],product['price'],order.order_id,customer.cust_id)
        db.session.add(prodorder)
        #add price from prodorder table to increcemt order price

        order.increment_order_total(prodorder.price)

        #decrement the avail quant of product
        current_product = Product.query.filter(Product.prod_id == product['prod_id']).first()
        current_product.decrement_quantity(product['quantity'])
        
    db.session.commit()
    return {
        'status':200,
        'message':'A new order was created'
    }
    

@api.route('/order/update/<order_id>',methods=['PUT','POST'])
@jwt_required()
def update_order(order_id):

    data=request.json
    new_quantity = int(data['quantity'])
    prod_id = data['prod_id']
    print(prod_id)
    prodorder = ProdOrder.query.filter(ProdOrder.order_id ==order_id,ProdOrder.prod_id==prod_id).first()
    order = Order.query.get(order_id)
    product = Product.query.get(prod_id)
    print(f"PRODORDER: {prodorder}")
    prodorder.set_price(product.price,new_quantity)

    diff = abs(prodorder.quantity - new_quantity)

    if prodorder.quantity < new_quantity:
        product.decrement_quantity(diff)
        order.increment_order_total(prodorder.price)

    elif prodorder.quantity > new_quantity:
        product.increment_quantity(diff)
        order.decrement_order_total(prodorder.price)


    prodorder.update_quantity(new_quantity)

    db.session.commit()

    return {

        'status':200,
        'message':"Order was successfully updated"
    }
    

#create DELETE route for orders
@api.route('/order/delete/<order_id>',methods=['DELETE'])
@jwt_required()
def delete_item_order(order_id):
    
    data = request.json
    prod_id = data['prod_id']
    
    prodorder = ProdOrder.query.filter(ProdOrder.order_id == order_id, ProdOrder.prod_id == prod_id).first()

    order= Order.query.get(order_id)
    product = Product.query.get(prod_id)

    order.decrement_order_total(prodorder.price)
    product.increment_quantity(prodorder.quantity)

    db.session.delete(prodorder)
    db.session.commit()

    return{
        'status':200,
        'message':"Order Delete Success"
    }
