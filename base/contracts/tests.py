from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from base.contracts.models import Rate, Contract
from base.sensors.models import Consumer, Sensor, Producer

from datetime import date, time
from django.urls import reverse


# Create your tests here.
class RateTest(TestCase):
    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('username', 'Pas$w0rd', is_staff=True)

    # test for flexible rate
    def test_create_flexible_rate(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        response = factory.post(path="/rates/",
                                data={"name": "Tarif1", "price": 5, "reduced_price": 4, "flexible": True,
                                      "start_time": time(hour=13, minute=14, second=31), 
                                      "end_time": time(hour=14, minute=14, second=31), 
                                      "start_date": date(year=2020, month=1, day=31),
                                      "end_date": date(year=2021, month=1, day=31)}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rate.objects.get(name="Tarif1").price, 5)

    # test for non-flexible rate
    def test_create_non_flexible_rate(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        response = factory.post(path="/rates/",
                                data={"name": "Tarif2", "price": 3, "reduced_price": 2, "flexible": False,
                                      "start_time": None, 
                                      "end_time": None, 
                                      "start_date": None,
                                      "end_date": None}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rate.objects.get(name="Tarif2").start_date, None)


producer_dump = {"name": "TestProd", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
class ContractTest(TestCase):
    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('cons_test', 'Pas$w0rd', is_staff=True)

        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        Sensor.objects.create(device_id=23142, type="CM")
        Rate.objects.create(name="GoGreen", price=40, reduced_price=35, flexible= True, start_time= "00:00", start_date= "2023-02-01")
        Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)  


    def test_create(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)

        cm = Sensor.objects.get(device_id=23142)
        rate = Rate.objects.get(name="GoGreen")
        prod = Producer.objects.get(name="TestProd")

        # Makes cm json serializable
        cm_dict = {
            'device_id': cm.device_id,
            'type': cm.type,
        }
        # Fetches URLs of the objects
        rate_url = reverse('rate-detail', args=[rate.pk])
        prod_url = reverse('producer-detail', args=[prod.pk])

        response1 = factory.post(path="/consumers/",
                                data={"name": "TestConsumer", "email": "t@t.de", "phone": "0004123420", "user": {
                                    "username": "TestC", "password": "sakdhdk124"
                                    }, "producer": prod_url, "sensor": cm_dict, "rates": [rate_url]}, format="json")
        
        # Check if consumer was created
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(Consumer.objects.get(name="TestConsumer").user.username, "TestC")
        self.assertEqual(Consumer.objects.get(name="TestConsumer").sensor.device_id, 23142)

        # Check if contract was created
        response1 = factory.get(path="/contracts/")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(Contract.objects.get(id=1).id,1)