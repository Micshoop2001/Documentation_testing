from application.extensions import ma
from application.models import Service_tickets


class MechanicSummarySchema(ma.Schema):
    id = ma.Integer()
    name = ma.String()
    email = ma.String()
    phone = ma.Integer()
class InventorySummarySchema(ma.Schema):
    id = ma.Integer()
    name = ma.String()
    price = ma.Float()

class Service_ticketsSchema(ma.SQLAlchemyAutoSchema):
    mechanics = ma.Nested(MechanicSummarySchema, many=True)
    inventory = ma.Nested(InventorySummarySchema, many=True)
    class Meta:
        model = Service_tickets
        include_fk = True
        load_instance = False

class Edit_Service_ticketsSchema(ma.Schema):
    additional_mechanic_id = ma.List(ma.Integer(), required=False)
    remove_mechanic_id = ma.List(ma.Integer(), required=False)
    additional_part_id = ma.List(ma.Integer(), required=False)
    remove_part_id = ma.List(ma.Integer(), required=False)
    
    class Meta:
        fields = ("additional_mechanic_id", "remove_mechanic_id", 
                  "additional_part_id", "remove_part_id")
        
Service_ticket_schema =Service_ticketsSchema()
Service_tickets_schema = Service_ticketsSchema(many=True)
Edit_Service_tickets_Schema = Edit_Service_ticketsSchema()