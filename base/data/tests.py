from datetime import datetime

from base.contracts.models import Rate
from base.data.models import Production, Consumption
from base.sensors.models import Sensor, Producer, Consumer
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

producer_dump = {"name": "T", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
consumer_dump = {"name": "t", "email": "t@t.de", "phone": "0004123420", }


# Create your tests here.
class TestData(TestCase):

    def setUp(self) -> None:
        User.objects.create_user('admin', 'Pas$w0rd', is_staff=True)
        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        prod = Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)

        rate = Rate.objects.create(price=40, reduced_price=35)

        # Create first user and his consumption sensor
        u1 = User.objects.create(username="max", password="sakhdk124")
        s1 = Sensor.objects.create(device_id=23142, type="CM")
        con1 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s1, user=u1)
        con1.rates.add(rate)
        con1.save()

        u2 = User.objects.create(username="gertrude", password="sakhdk124")
        s2 = Sensor.objects.create(device_id=51513, type="CM")
        con2 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s2, user=u2)
        con2.rates.add(rate)
        con2.save()

    def test_setup_no_data(self):
        user = User.objects.get(username="admin")
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)

        res = factory.post("/setup/", data={
            'producer_id': "1",
            'timestamp': "2023-02-23T10:00:00"
        }, format='json')
        production = Production.objects.first()
        self.assertEqual(datetime.strftime(production.time, "%Y-%m-%dT%H:%M:%S"), "2023-02-23T10:00:00")
        self.assertEqual(production.produced, 0)
        self.assertEqual(production.used, 0)
        self.assertEqual(production.grid_feed_in, 0)
        self.assertEqual(production.grid_meter_reading, 0)
        self.assertEqual(production.production_meter_reading, 0)
        c1 = Consumption.objects.get(consumer_id=1)
        self.assertEqual(datetime.strftime(c1.time, "%Y-%m-%dT%H:%M:%S"), "2023-02-23T10:00:00")
        self.assertEqual(c1.consumption, 0)
        self.assertEqual(c1.self_consumption, 0)
        self.assertEqual(c1.grid_consumption, 0)
        self.assertEqual(c1.meter_reading, 0)
        self.assertEqual(c1.saved, 0)
        c2 = Consumption.objects.get(consumer_id=1)
        self.assertEqual(datetime.strftime(c2.time, "%Y-%m-%dT%H:%M:%S"), "2023-02-23T10:00:00")
        self.assertEqual(c2.consumption, 0)
        self.assertEqual(c2.self_consumption, 0)
        self.assertEqual(c2.grid_consumption, 0)
        self.assertEqual(c2.meter_reading, 0)
        self.assertEqual(c2.saved, 0)

    def test_setup_prior_data_exist(self):
        prdctn = Production.objects.create(time=datetime.now(), produced=0, used=0, production_meter_reading=0,
                                           grid_meter_reading=0, producer=Producer.objects.first(), grid_feed_in=0)

        user = User.objects.get(username="admin")
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        res = factory.post("/setup/", data={
            'producer_id': "1",
            'timestamp': "2023-02-23T10:00:00"
        }, format='json')
        self.assertEqual(res.status_code, 208)

    def test_setup_wrong_producer_id(self):
        user = User.objects.get(username="admin")
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        res = factory.post("/setup/", data={
            'producer_id': "12",
            'timestamp': "2023-02-23T10:00:00"
        }, format='json')
        self.assertEqual(res.status_code, 404)

    def test_setup_missing_data(self):
        user = User.objects.get(username="admin")
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        res = factory.post("/setup/", data={
            'producer_id': "12"
        }, format='json')
        self.assertEqual(res.status_code, 400)
        res = factory.post("/setup/", data={
            'timestamp': "2023-02-23T10:00:00"
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_setup_wrong_time_format(self):
        user = User.objects.get(username="admin")
        factory = APIClient(enforce_csrf_checks=False)
        factory.force_login(user=user)
        res = factory.post("/setup/", data={
            'producer_id': "12",
            'timestamp': "23.01.2023T10:00:00"
        }, format='json')
        self.assertEqual(res.status_code, 400)
