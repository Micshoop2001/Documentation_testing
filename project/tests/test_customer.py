from application import create_app
from application.models import db, Customers
#from datetime import datetime
from application.utils.util import encode_token
import unittest
print(">>> test_customer.py LOADED")
print(">>> create_app reference:", create_app)

class TestCustomer(unittest.TestCase):
    
    def setUp(self):
        
        self.app = create_app('TestingConfig')
        #self.app_context = self.app.app_context()
        #self.app_context.push()
        self.customer1 = Customers(name="test_user", email="test@email.com", phone=2222222 , password='test')
        self.customer2 = Customers(name="test_user2", email="test2@email.com", phone=3333333 , password='test2')
        print("ACTIVE DB:", self.app.config["SQLALCHEMY_DATABASE_URI"])
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer1)
            db.session.add(self.customer2)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
        
    ############################################################################
    def login_helper(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }
        response = self.client.post('/customers/login', json=credentials)
        return response.json['auth_token']
    ############################################################################
    
    def test_create_customer(self): #Post new customer
        headers = {'Authorization': "Bearer " + self.login_helper()}
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
           	"phone": 4444444,
            "password": "123"
        }
        response = self.client.post('/customers/', json=customer_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
    
    ############################################################################
    
    def test_get_customer(self): #Get customers
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'test_user')
    
    ############################################################################
        
    def test_invalid_creation(self): #Post new customer without email, which is required
        customer_payload = {
            "name": "John Doe",
            "phone": 1111111,
            "password": "123"       
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
    
    ############################################################################
        
    def test_login_customer(self): #test login of customer from setup, return token for use in other tests  
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['auth_token']
    
    ############################################################################
    
    def test_invalid_login(self): #test bad login
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')
    
    ############################################################################
        
    def test_update_customer(self): #test PUT updating customer info
        update_payload = {
            "name": "Peter",
            "phone": 2222222,
            "email": "test@email.com",
            "password": "newpassword"
        }

        headers = {'Authorization': "Bearer " + self.login_helper()}

        response = self.client.put('/customers/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'test@email.com')
        
    ############################################################################
    
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.login_helper()}

        response = self.client.delete('/customers/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "successfully deleted customer 2")
        
    ############################################################################
    
    def test_delete_login_customer(self):
        headers = {'Authorization': "Bearer " + self.login_helper()}

        response = self.client.delete('/customers/login', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'successfully deleted customer 1')
        
    ############################################################################
    
    