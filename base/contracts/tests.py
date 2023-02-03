from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APIClient
from base.contracts.models import Rate
from base.sensors.models import Consumer, Sensor
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


class ContractTest(TestCase):
    def setUp(self) -> None:
        User.objects.create_user('username2', 'Pas$w0rd', is_staff=True)

        Rate.objects.create(name="GreatRate", price=4, reduced_price=3, flexible=False)
        sensor1 = Sensor.objects.create(device_id=55555, type="CM")
        Consumer.objects.create(sensor=sensor1, name="SolarSören", email="solarsören69@email.de", phone="69696969")

    def test_create_contract(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)

        rate = Rate.objects.get(name="GreatRate")
        consumer = Consumer.objects.get(name="SolarSören")

        # Fetches URLs of the objects
        rate_url = reverse('rate-detail', args=[rate.pk])
        consumer_url = reverse('consumer-detail', args=[consumer.pk])

        response = factory.post(path="/contracts/",
                                data={rate:rate_url, consumer:consumer_url}, format='json')
        self.assertEqual(response.status_code, 201)