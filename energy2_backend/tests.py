from django.test import TestCase
from energy2_backend.urls import *
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from input.views import InputHandler
from decimal import Decimal
from pprint import pprint

producer_dump = {"name": "T", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
consumer_dump = {"name": "t", "email": "t@t.de", "phone": "0004123420", }


# Create your tests here.
class FinalTest(TestCase):
    time_now = datetime.now()
    time_now = datetime(day=12, month=1, year=2023, hour=10, minute=0)  # time_now = 10:00

    '''Initial setup of objects'''

    def setUp(self) -> None:
        time_now = self.time_now

        # Create production and grid sensors, producer object and production object
        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        prod = Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)
        prdctn = Production.objects.create(time=time_now, produced=0, used=0, production_meter_reading=0,
                                           grid_meter_reading=0, producer=prod, grid_feed_in=0)

        # Create rate
        rate = Rate.objects.create(price=40, reduced_price=35)

        # Create first user and his consumption sensor
        u1 = User.objects.create(username="max", password="sakhdk124")
        s1 = Sensor.objects.create(device_id=23142, type="CM")
        con1 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s1, user=u1)
        con1.rates.add(rate)
        con1.save()
        cons1 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con1,
                                           time=time_now, production=prdctn, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        # Create second user and her consumption sensor
        u2 = User.objects.create(username="gertrude", password="sakhdk124")
        s2 = Sensor.objects.create(device_id=51513, type="CM")
        con2 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s2, user=u2)
        con2.rates.add(rate)
        con2.save()
        cons2 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con2,
                                           time=time_now, production=prdctn, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

    def test_presentation(self):
        Consumer.objects.get(id=2).delete()
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)
        # factory.force_login(user=user)
        response = factory.post("/input/", data={
            'device_id': 123123,  # PV
            'source_time': self.time_now + timedelta(minutes=15),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 23142,  # Max
            'source_time': self.time_now + timedelta(minutes=17),
            'parsed': {
                'Lieferung_Gesamt_kWh': 0,
                'Bezug_Gesamt_kWh': 1,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=20),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 23142,  # Max
            'source_time': self.time_now + timedelta(minutes=25),
            'parsed': {
                'Lieferung_Gesamt_kWh': 0,
                'Bezug_Gesamt_kWh': 1.5,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 123123,  # PV
            'source_time': self.time_now + timedelta(minutes=30),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1.5,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 123123,  # PV
            'source_time': self.time_now + timedelta(minutes=45),
            'parsed': {
                'Lieferung_Gesamt_kWh': 2,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 23142,  # Max
            'source_time': self.time_now + timedelta(minutes=55),
            'parsed': {
                'Lieferung_Gesamt_kWh': 0,
                'Bezug_Gesamt_kWh': 2,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=60),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1.5,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
