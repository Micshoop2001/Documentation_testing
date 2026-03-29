from urllib import response

from application.__init__ import create_app
from application.models import db, Service_tickets, Mechanics, Inventory
from application.utils.util import encode_token
import unittest
from datetime import date

class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.service_tickets1 = Service_tickets(service_date=date(1976, 10, 12), VIN="ABC", 
                                                service_desc="stuff stuff stuff", customers_id=1)
        self.service_tickets2 = Service_tickets(service_date=date(1990, 10, 12), VIN="DEF", 
                                                service_desc="more stuff", customers_id=2)
        self.mechanic1 = Mechanics(name="Test Mechanic 1", email="test1@example.com", phone=1234567890, salary=50000.00)
        self.mechanic2 = Mechanics(name="Test Mechanic 2", email="test2@example.com", phone=0000000000, salary=50000.00 )
        self.part1 = Inventory(name="Test Part 1", price=10.99)
        self.part2 = Inventory(name="Test Part 2", price=5.99)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.service_tickets1)
            db.session.add(self.service_tickets2)
            db.session.add(self.mechanic1)
            db.session.add(self.mechanic2)
            db.session.add(self.part1)  
            db.session.add(self.part2)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    ####################################################################################
        
    def test_create_service_ticket(self): #Post new service ticket
        headers = {'Authorization': f"Bearer {self.token}"}
        service_ticket_payload = {
            "service_date": f'{date(2000, 10, 12)}',
            "VIN": "GHI",
            "service_desc": "even more stuff",
            "customers_id": 1
        }
        response = self.client.post('/service-tickets/', json=service_ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 201)

        data = response.json

        self.assertEqual(data['VIN'], "GHI")
        self.assertEqual(data['service_desc'], "even more stuff")
        self.assertEqual(data['customers_id'], 1)
        self.assertEqual(data['service_date'], "2000-10-12")

        self.assertIn('mechanics', data)
        self.assertIn('inventory', data)

    ####################################################################################
    
    def test_invalid_service_ticket(self): #Post invalid ticket 
        headers = {'Authorization': f"Bearer {self.token}"}
        service_ticket_payload = {
            "service_date": f'{date(2000, 10, 12)}',
            "service_desc": "even more stuff",
            "customers_id": 1
        }
        response = self.client.post('/service-tickets/', json=service_ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['VIN'], ['Missing data for required field.'])

    ####################################################################################

    def test_get_service_tickets(self): #Get service tickets
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['VIN'], 'ABC')

    ####################################################################################

    def test_get_my_tickets(self): #Get my tickets
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.get('/service-tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["tickets"]), 1)
        self.assertEqual((response.json["tickets"]), [1])

    ####################################################################################
    
    def test_update_mechanic(self): #test PUT updating mechanic info
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.put('/service-tickets/1/assign-mechanic/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)
    
    ####################################################################################
    
    def test_remove_mechanic(self): #test PUT removing mechanic info
        headers = {'Authorization': f"Bearer {self.token}"}
        self.client.put('/service-tickets/1/assign-mechanic/1', headers=headers)
        response = self.client.put('/service-tickets/1/remove-mechanic/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 0)
    
    ####################################################################################

    def test_add_remove_mechanic(self): #test add or remove mechanic
        headers = {'Authorization': f"Bearer {self.token}",
                   'Content-Type': 'application/json'}
        add_payload = {"additional_mechanic_id": [1], "remove_mechanic_id": []}

        response = self.client.put('/service-tickets/1/edit', headers=headers, json=add_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)
        
        remove_payload = {"additional_mechanic_id": [], "remove_mechanic_id": [1]}

        response = self.client.put('/service-tickets/1/edit', headers=headers, json=remove_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 0)
        
    ####################################################################################

    def test_add_remove_part(self): #test add or remove mechanic
        headers = {'Authorization': f"Bearer {self.token}",
                   'Content-Type': 'application/json'}
        add_payload = {"additional_part_id": [1], "remove_part_id": []}

        response = self.client.put('/service-tickets/1/parts', headers=headers, json=add_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['inventory']), 1)
        self.assertEqual(response.json['inventory'][0]['id'], 1)
        
        remove_payload = {"additional_part_id": [], "remove_part_id": [1]}

        response = self.client.put('/service-tickets/1/parts', headers=headers, json=remove_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['inventory']), 0)
        
    ####################################################################################
    
    