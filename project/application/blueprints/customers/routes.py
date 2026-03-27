from .Schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customers, db
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required
from . import customers_bp

#POST '/login' : passing in email and password, validated by login_schema   
@customers_bp.route("/login", methods=['POST']) #test
@limiter.limit("1000/hour")
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query =select(Customers).where(Customers.email == email) 
    customer = db.session.execute(query).scalar_one_or_none() #Query customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the email, validate the password
        auth_token = encode_token(customer.id)
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

@customers_bp.route('/login', methods=['DELETE']) #test
@token_required
def delete_customer_token(user_id): #Recieving user_id from the token
    query = select(Customers).where(Customers.id == user_id)
    customer = db.session.execute(query).scalars().first()
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {user_id}"})

#POST '/' : Creates a new Customer
@customers_bp.route('/', methods=['POST']) #test
@limiter.limit("15 per day")

def create_customer():
    try:
        customer = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customers(name=customer['name'], 
                    phone=customer['phone'], 
                    email=customer['email'],
                    password=customer['password'])
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201    
 
#Apply Pagination to GET Customers route. 
#GET '/': Retrieves all Customers
@customers_bp.route("/", methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
def get_customers():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Customers)
        customers = db.paginate(query, page=page, per_page=per_page).items 
    except:
        query = select(Customers)
        customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)


#PUT '/<int:id>': Updates a specific Customer based on the id passed in through the url.
@customers_bp.route('/<int:id>', methods=['PUT']) #test
@limiter.limit("50/day")
@token_required
def update_customer(id):
    customer = db.session.get(Customers, id)

    if not customer:
        return jsonify({"message": "customer id not found"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.phone = customer_data['phone']
    customer.email = customer_data['email']

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#DELETE '/<int:id': Deletes a specific customer based on the id passed in through the url.
@customers_bp.route('/<int:id>', methods=['DELETE']) #test
@limiter.limit("50/day")
@token_required
def delete_customer(id):
    customer = db.session.get(Customers, id)
    if not customer:
        return jsonify({"message": "customer id not found"}), 404 
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {id}"}), 200


