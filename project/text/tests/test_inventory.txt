from application.__init__ import create_app
from application.models import db, Inventory
#from datetime import datetime
from application.utils.util import encode_token
import unittest

class TestInventory(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.inventory1 = Inventory(name="test_part", price=100.00)
        self.inventory2 = Inventory(name="test_part2", price=200.00)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory1)
            db.session.add(self.inventory2)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
    
    ############################################################################
    
    def test_create_inventory(self): #Post new inventory item
        headers = {'Authorization': f"Bearer {self.token}"}
        inventory_payload = {"name": "test_part3", "price": 300.00}
        response = self.client.post('/inventory/', json=inventory_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "test_part3")
        
    ############################################################################
    
    def test_get_inventory(self): #Get inventory items
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'test_part')
        
    ############################################################################
    
    def test_update_inventory(self): #test PUT updating inventory info
        update_payload = {"name": "wheel", "price": 150.00}
        headers = {'Authorization': f"Bearer {self.token}"}

        response = self.client.put('/inventory/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'wheel') 
        self.assertEqual(response.json['price'], 150.00)
        
    ############################################################################
    
    def test_delete_inventory(self):
        headers = {'Authorization': f"Bearer {self.token}"}

        response = self.client.delete('/inventory/2', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'successfully deleted inventory 2')
        
    ############################################################################