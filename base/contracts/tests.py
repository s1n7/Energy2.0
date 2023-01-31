from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APIClient
from base.contracts.models import Rate
from datetime import date, time, datetime


# Create your tests here.
class ContractTest(TestCase):
    def setUp(self) -> None:
        # to login in test, user has to be created in test db
        User.objects.create_user('username', 'Pas$w0rd', is_staff=True)

    def test_create(self):
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        response = factory.post(path="/rates/",
                                data={"name": "Tarif1", "price": 5, "reduced_price": 10, "flexible": True,
                                      "start_time": time(hour=13, minute=14, second=31), 
                                      "end_time": time(hour=14, minute=14, second=31), 
                                      "start_date": date(year=2020, month=1, day=31),
                                      "end_date": date(year=2021, month=1, day=31)}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rate.objects.get(name="Tarif1").price, 5)