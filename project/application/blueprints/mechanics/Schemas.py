from application.extensions import ma
from application.models import Mechanics

class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics

mechanic_schema =MechanicsSchema()
mechanics_schema = MechanicsSchema(many=True)