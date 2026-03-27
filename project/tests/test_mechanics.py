from application.__init__ import create_app
from application.models import db, Mechanics
from application.utils.util import encode_token
import unittest


class TestMechanics(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic1 = Mechanics(name="test_mechanic", email="test_mechanic@email.com", phone=4444444, salary=5)   
        self.mechanic2 = Mechanics(name="test_mechanic2", email="test_mechanic2@email.com", phone=5555555, salary=6)   
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic1)
            db.session.add(self.mechanic2)
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
    
    def test_create_mechanic(self): #Post new mechanic
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        mechanic_payload = {"name": "John Doe", "email": "jd@email.com",
            "phone": 6666666, "salary": 6}
        response = self.client.post('/mechanics/', json=mechanic_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe") 
    
    ############################################################################
    
    def test_get_mechanic(self): #Get mechanics
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
    
    ############################################################################
        
    def test_update_mechanic(self): #test PUT updating mechanic info
        update_payload = {
            "name": "Peter",
            "phone": 8888888,
            "email": "p@email.com",
            "salary": 7
        }

        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.put('/mechanics/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'p@email.com')
        self.assertEqual(response.json['salary'], 7)
        
    ############################################################################
    
    def test_get_most_active_mechanic(self): #test GET most active mechanic
        response = self.client.get('/mechanics/most-active')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 3)
        self.assertEqual(len(response.json[0]['service_tickets']), 0)
        self.assertEqual(len(response.json[1]['service_tickets']), 0)
        self.assertEqual(len(response.json[2]['service_tickets']), 0)
    
    ############################################################################
    
    def test_delete_mechanic(self): #delete mechanic by id
        headers = {'Authorization': "Bearer " + self.test_login_customer()}

        response = self.client.delete('/mechanics/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'successfully deleted mechanic 3')
        
    ############################################################################
    
    