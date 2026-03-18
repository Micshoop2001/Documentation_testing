from application.__init__ import create_app
from application.models import db, Service_tickets, Mechanics, Inventory
#from datetime import datetime
from application.utils.util import encode_token
import unittest

class TestServiceTickets(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.service_tickets1 = Service_tickets(service_date="1976-10-12", VIN="ABC", 
                                                service_desc="stuff stuff stuff", customers_id=1)
        self.service_tickets2 = Service_tickets(service_date="1990-10-12", VIN="DEF", 
                                                service_desc="more stuff", customers_id=2)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.service_tickets1)
            db.session.add(self.service_tickets2)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    ####################################################################################
        
    def test_create_service_ticket(self): #Post new service ticket
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        service_ticket_payload = {
            "service_date": "2000-10-12",
            "VIN": "GHI",
            "service_desc": "even more stuff",
            "customers_id": 1
        }
        response = self.client.post('/service-tickets/', json=service_ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], "GHI")

    ####################################################################################
    
    def test_invalid_service_ticket(self): #Post invalid ticket 
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        service_ticket_payload = {
            "service_date": "2000-10-12",
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
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.get('/my-tickets/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["tickets"]), 1)
        self.assertEqual((response.json["tickets"]), [1])

    ####################################################################################
    
    def test_update_mechanic(self): #test PUT updating mechanic info
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.put('/service-tickets/1/assign-mechanic/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)
    
    ####################################################################################
    
    def test_remove_mechanic(self): #test PUT removing mechanic info
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.put('/service-tickets/1/remove-mechanic/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 0)
    
    ####################################################################################

    def test_add_remove_mechanic(self): #test add or remove mechanic
        headers = {'Authorization': "Bearer " + self.test_login_customer(),
                   'Content-Type': 'application/json'}
        add_payload = {"additional_mechanic_id": [1], "remove_mechanic_id": []}

        response = self.client.put('/service-tickets/1/edit', headers=headers, json=add_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)
        
        remove_payload = {"additional_mechanic_id": [], "remove_mechanic_id": [1]}

        response = self.client.put('/service-tickets/1/edit', headers=headers, json=remove_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        
    ####################################################################################

    def test_add_remove_part(self): #test add or remove mechanic
        headers = {'Authorization': "Bearer " + self.test_login_customer(),
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
    
    