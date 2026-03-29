from .Schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Inventory, db
from application.extensions import limiter, cache
from application.utils.util import token_required
from . import inventory_bp


#POST '/' : Creates a new Inventory item
@inventory_bp.route('/', methods=['POST']) #test
@limiter.limit("10/day")
@token_required
def create_inventory(user_id):
    try:
        inventory = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_inventory = Inventory(name=inventory['name'], 
                    price=inventory['price'])
    
    db.session.add(new_inventory)
    db.session.commit()

    return inventory_schema.jsonify(new_inventory), 201    
 
####################################################################################  
#GET '/': Retrieves all Inventory with pagination
@inventory_bp.route("/", methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
def get_inventory():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Inventory)
        inventory = db.paginate(query, page=page, per_page=per_page).items 
    except:
        query = select(Inventory)
        inventory = db.session.execute(query).scalars().all()

    return inventories_schema.jsonify(inventory)

#################################################################################### 
#PUT '/<int:id>': Updates a specific Inventory based on the id passed in through the url.
@inventory_bp.route('/<int:id>', methods=['PUT']) #test
@limiter.limit("100/day")
@token_required
def update_inventory(user_id, id):
    inventory = db.session.get(Inventory, id)

    if not inventory:
        return jsonify({"message": "inventory id not found"}), 404
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    inventory.name = inventory_data['name']
    inventory.price = inventory_data['price']

    db.session.commit()
    return inventory_schema.jsonify(inventory), 200
#################################################################################### 
#DELETE '/<int:id': Deletes a specific Inventory based on the id passed in through the url.
@inventory_bp.route('/<int:id>', methods=['DELETE']) #test
@limiter.limit("100/day")
@token_required
def delete_inventory(user_id, id):
    inventory = db.session.get(Inventory, id)
    if not inventory:
        return jsonify({"message": "inventory id not found"}), 404 
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({"message": f"successfully deleted inventory {id}"}), 200


