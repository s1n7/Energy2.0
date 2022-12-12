from django.test import TestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.auth.models import User
from base.sensors.models import Producer
from base.sensors.views import ProducerView
from django.urls import reverse


# Create your tests here.
class ProducerTest(TestCase):
    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('username', 'Pas$w0rd')

    def test_create(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        response = factory.post(path="/producers/", data={"name": "Test", "sensor": {
            "eui_id": 123,
            "device_id": 123
        }}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Producer.objects.get(name="Test").sensor.eui_id, 123)
