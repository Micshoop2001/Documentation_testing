from .Schemas import Service_ticket_schema, Service_tickets_schema, Edit_Service_tickets_Schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Service_tickets, Mechanics, Inventory, db
from application.extensions import limiter, cache
from application.utils.util import token_required
from . import service_tickets_bp

@service_tickets_bp.route("/", methods=['POST']) #test
@limiter.limit("50/day")
@token_required 
def create_service_ticket(user_id):
    try:
        service_ticket_data = Service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_service_ticket = Service_tickets(
            service_date=service_ticket_data['service_date'], 
            VIN=service_ticket_data['VIN'], 
            service_desc=service_ticket_data['service_desc'],
            customers_id=service_ticket_data['customers_id'])
    
    db.session.add(new_service_ticket)
    db.session.commit()

    return Service_ticket_schema.jsonify(new_service_ticket), 201     
####################################################################################
@service_tickets_bp.route("/<ticket_id>/assign-mechanic/<mechanic_id>", methods=['PUT']) #test
@limiter.limit("50/day") 
@token_required 
def update_mechanic(ticket_id, mechanic_id, user_id):
    service_ticket_data = db.session.get(Service_tickets, ticket_id)
    mechanic_data = db.session.get(Mechanics, mechanic_id)
    if not service_ticket_data:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic_data:
        return jsonify({"error": "Mechanic not found"}), 404
    if mechanic_data in service_ticket_data.mechanics:
        return jsonify({"message": "Mechanic already in list"}), 200
    service_ticket_data.mechanics.append(mechanic_data)
    db.session.commit()
    return Service_ticket_schema.jsonify(service_ticket_data), 200
####################################################################################    
@service_tickets_bp.route("/<ticket_id>/remove-mechanic/<mechanic_id>", methods=['PUT']) #test
@limiter.limit("50/day") 
@token_required
def remove_mechanic(ticket_id, mechanic_id, user_id):
    service_ticket_data = db.session.get(Service_tickets, ticket_id)
    mechanic_data = db.session.get(Mechanics, mechanic_id)
    if not service_ticket_data:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic_data:
        return jsonify({"error": "Mechanic not found"}), 404
    if mechanic_data not in service_ticket_data.mechanics:
        return jsonify({"message": "Mechanic not in list"}), 404
    service_ticket_data.mechanics.remove(mechanic_data)
    db.session.commit()
    return Service_ticket_schema.jsonify(service_ticket_data), 200    
####################################################################################    
#GET '/': Retrieves all service tickets.
@service_tickets_bp.route("/", methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
def get_service_tickets():
    query = select(Service_tickets)
    service_tickets = db.session.execute(query).scalars().all()

    return Service_tickets_schema.jsonify(service_tickets)    
####################################################################################
#GET '/my-tickets': requires a Bearer Token authorization  needs to be checked in postman!!
@service_tickets_bp.route('/my-tickets', methods=['GET']) #test
@limiter.limit("100/hour")
@cache.cached(timeout=60)
@token_required
def get_my_tickets(user_id):
    tickets = db.session.execute(
        select(Service_tickets).where(Service_tickets.customers_id == user_id)
    ).scalars().all()

    return jsonify({"tickets": [t.id for t in tickets]}), 200
    
####################################################################################
#Add an update route to your service_ticket blueprint to add and remove mechanics from a ticket.
#PUT '/<int:ticket_id>/edit' : Takes in remove_ids, and add_ids
#Use id's to look up the mechanic to append or remove them from the ticket.mechanics list
@service_tickets_bp.route("/<ticket_id>/edit", methods=['PUT']) #test
@limiter.limit("500/hour")
@token_required
def add_remove_mechanics(ticket_id, user_id):
    try:
        Edit_Service_data = Edit_Service_tickets_Schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(Service_tickets).where(Service_tickets.id == ticket_id, 
                            Service_tickets.customers_id == user_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in Edit_Service_data['additional_mechanic_id']:
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for mechanic_id in Edit_Service_data['remove_mechanic_id']:
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
    db.session.commit()
    return Service_ticket_schema.jsonify(service_ticket), 200

####################################################################################
@service_tickets_bp.route("/<ticket_id>/parts", methods=['PUT']) #test
@limiter.limit("500/day")
@token_required
def add_remove_part(ticket_id, user_id):
    try:
        Edit_Service_data = Edit_Service_tickets_Schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(Service_tickets).where(Service_tickets.id == ticket_id, 
                                Service_tickets.customers_id == user_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for part_id in Edit_Service_data['additional_part_id']:
        query = select(Inventory).where(Inventory.id == part_id)
        part = db.session.execute(query).scalars().first()
        if part and part not in service_ticket.inventory:
            service_ticket.inventory.append(part)

    for part_id in Edit_Service_data['remove_part_id']:
        query = select(Inventory).where(Inventory.id == part_id)
        part = db.session.execute(query).scalars().first()
        if part and part in service_ticket.inventory:
            service_ticket.inventory.remove(part)
    db.session.commit()
    return Service_ticket_schema.jsonify(service_ticket), 200

