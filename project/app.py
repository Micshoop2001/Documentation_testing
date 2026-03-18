from application import create_app
from application.models import db

def create_app_instance():
    app = create_app('DevelopmentConfig')
    with app.app_context():
        db.create_all()
    return app
'''
app = create_app_instance()

if __name__ == "__main__":
    app.run()
'''