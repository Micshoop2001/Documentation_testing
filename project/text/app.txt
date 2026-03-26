from application import create_app
from application.models import db
    
app = create_app('DevelopmentConfig')    
print(">>> app.py create_app reference:", create_app)
    
# Create the table
with app.app_context():
    #db.drop_all() #Drop all tables to reset the database
    db.create_all()

if __name__ == "__main__":
    app.run()