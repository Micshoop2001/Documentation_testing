from application.extensions import ma
from application.models import Customers

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)
login_schema = CustomersSchema(only=['email', 'password'])