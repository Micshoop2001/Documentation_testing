from .Schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Mechanics, db
from application.extensions import limiter, cache
from application.utils.util import token_required
from . import mechanics_bp
    

#POST '/' : Creates a new Mechanic
@mechanics_bp.route('/', methods=['POST']) #test
@limiter.limit("50/day")
@token_required
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_mechanic = Mechanics(name=mechanic_data['name'], 
                    phone=mechanic_data['phone'], 
                    email=mechanic_data['email'],
                    salary=mechanic_data['salary'])
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201    
 
 #GET '/': Retrieves all Mechanics
@mechanics_bp.route("/", methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
def get_mechanics():
    query = select(Mechanics)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)

#PUT '/<int:id>':  Updates a specific Mechanic based on the id passed in through the url.
@mechanics_bp.route('/<int:id>', methods=['PUT']) #test
@limiter.limit("50/day")
@token_required
def update_mechanic(id):
    mechanic = db.session.get(Mechanics, id)

    if not mechanic:
        return jsonify({"message": "mechanic id not found"}), 404
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    mechanic.name = mechanic_data['name']
    mechanic.phone = mechanic_data['phone']
    mechanic.email = mechanic_data['email']
    mechanic.salary = mechanic_data['salary']

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#DELETE '/<int:id': Deletes a specific Mechanic based on the id passed in through the url.
@mechanics_bp.route('/<int:id>', methods=['DELETE']) #test
@limiter.limit("5/day")
@token_required
def delete_mechanic(id):
    mechanic = db.session.get(Mechanics, id)
    if not mechanic:
        return jsonify({"message": "mechanic id not found"}), 404
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"successfully deleted mechanic {id}"}), 200


#Create an endpoint in mechanics blueprint that returns a list of mechanics in order of who has worked on the most tickets
@mechanics_bp.route('/most-active', methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
def get_most_active_mechanics():
    query = select(Mechanics)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda m: len(m.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics)

