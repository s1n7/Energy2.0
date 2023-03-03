import pprint

from django.test import TestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from base.sensors.models import Sensor, Producer, Consumer
from base.sensors.views import ProducerView
from base.contracts.models import Rate
from django.urls import reverse


# Create your tests here.
class ProducerTest(TestCase):
    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('username', 'Pas$w0rd', is_staff=True)

    def test_create(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        response = factory.post(path="/producers/",
                                data={"name": "Test", "street": "t", "zip_code": "t", "city": "2",
                                      "peak_power": 1, "production_sensor": {
                                        "device_id": 12523,
                                        "type": "PM"
                                    }, "grid_sensor": {
                                        "device_id": 12323,
                                        "type": "GM"
                                    }}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Producer.objects.get(name="Test").grid_sensor.device_id, 12323)
        self.assertEqual(Producer.objects.get(name="Test").production_sensor.device_id, 12523)


producer_dump = {"name": "TestProd", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}


class ConsumerTest(TestCase):

    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('cons_test', 'Pas$w0rd', is_staff=True)

        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        self.cm = {'device_id': 643523, 'type': "CM"}
        Rate.objects.create(name="GoGreen", price=40, reduced_price=35, flexible=True, start_time="00:00",
                            start_date="2023-02-01")
        Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)

    def test_create(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)

        cm = self.cm
        rate = Rate.objects.get(name="GoGreen")
        prod = Producer.objects.get(name="TestProd")

        # Makes cm json serializable
        cm_dict = {
            'device_id': cm['device_id'],
            'type': cm['type'],
        }
        # Fetches URLs of the objects
        rate_url = reverse('rate-detail', args=[rate.pk])
        prod_url = reverse('producer-detail', args=[prod.pk])

        response3 = factory.post(path="/consumers/",
                                 data={"name": "TestConsumer", "email": "t@t.de", "phone": "0004123420", "user": {
                                     "username": "TestC", "password": "sakdhdk124"
                                 }, "producer": prod_url, "sensor": cm_dict, "rates": [rate_url]}, format="json")
        self.assertEqual(response3.status_code, 201)
        self.assertEqual(Consumer.objects.get(name="TestConsumer").email, "t@t.de")
        self.assertEqual(Consumer.objects.get(name="TestConsumer").user.username, "TestC")
        self.assertEqual(Consumer.objects.get(name="TestConsumer").sensor.device_id, cm['device_id'])
        self.assertEqual(Consumer.objects.get(name="TestConsumer").producer.name, "TestProd")
        self.assertEqual(Consumer.objects.get(name="TestConsumer").rates.first().price, 40)
