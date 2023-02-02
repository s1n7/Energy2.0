from django.test import TestCase
from energy2_backend.urls import *
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from input.views import InputHandler
from decimal import Decimal

producer_dump = {"name": "T", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
consumer_dump = {"name": "t", "email": "t@t.de", "phone": "0004123420", }


# Create your tests here.
class InputTest(TestCase):
    time_now = datetime.now()
    time_now = datetime(day=12, month=1, year=2023, hour=10, minute=0)

    def setUp(self) -> None:
        time_now = self.time_now
        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        print(Sensor.objects.all())
        prod = Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)
        prdctn = Production.objects.create(time=time_now, produced=0, used=0, production_meter_reading=0,
                                           grid_meter_reading=0, producer=prod, grid_feed_in=0)

        rate = Rate.objects.create(price=40, reduced_price=35)

        u1 = User.objects.create(username="1", password="sakhdk124")
        s1 = Sensor.objects.create(device_id=23142, type="CM")
        con1 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s1, user=u1)
        con1.rates.add(rate)
        con1.save()
        cons1 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con1,
                                           time=time_now, production=prdctn, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        u2 = User.objects.create(username="2", password="sakhdk124")
        s2 = Sensor.objects.create(device_id=51513, type="CM")
        con2 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s2, user=u2)
        con2.rates.add(rate)
        con2.save()
        cons2 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con2,
                                           time=time_now, production=prdctn, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

    def test_create_consumptions(self):
        time_now = self.time_now
        new_production = Production.objects.create(time=time_now + timedelta(minutes=15), produced=0.2, used=0.15,
                                                   production_meter_reading=0.2, grid_feed_in=0.05,
                                                   grid_meter_reading=0.05, producer=Producer.objects.first())
        new_reading = Reading.objects.create(energy=0.2, power=0, sensor=Consumer.objects.get(id=1).sensor,
                                             time=time_now + timedelta(minutes=23))
        ih = InputHandler(request=None, producer=Producer.objects.first())
        self.assertEqual(ih._check_for_new_consumption(), False)
        new_reading_2 = Reading.objects.create(energy=0.5, power=0, sensor=Consumer.objects.get(id=2).sensor,
                                               time=time_now + timedelta(minutes=25))
        self.assertEqual(ih._check_for_new_consumption(), True)                          
        new_production_reading = Reading.objects.create(energy=0.3, power=0, time=time_now + timedelta(minutes=30),
                                                        sensor=Producer.objects.first().production_sensor)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), False)
        new_grid_reading = Reading.objects.create(energy=0.1, power=0, time=time_now + timedelta(minutes=35),
                                                  sensor=Producer.objects.first().grid_sensor)
        print(Producer.objects.get(id=1).last_production_reading)
        print(Producer.objects.get(id=1).last_grid_reading)
        self.assertEqual(ih._check_for_new_production(), False)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), True)

    def test_ppt_example(self):
        time_now = self.time_now
        ih = InputHandler(request=None, producer=Producer.objects.first())

        new_production_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=15),
                                                        sensor=Producer.objects.first().production_sensor)
        new_grid_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=20),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), True)
        ih._create_new_production()
        self.assertEqual(Production.objects.last().used, 0.25)
        max_reading = new_reading = Reading.objects.create(energy=0.5, power=0,
                                                           sensor=Consumer.objects.get(id=1).sensor,
                                                           time=time_now + timedelta(minutes=21))
        gertrude_reading = new_reading = Reading.objects.create(energy=1, power=0,
                                                                sensor=Consumer.objects.get(id=2).sensor,
                                                                time=time_now + timedelta(minutes=25))
        ih.handle_input()
        new_production_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=30),
                                                        sensor=Producer.objects.first().production_sensor)
        new_grid_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=35),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        print(Reading.objects.all())
        self.assertEqual(ih._check_for_new_production(), True)
        ih._create_new_production()
        self.assertEqual(Production.objects.last().used, 0)

    def test_ppt_network(self):
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
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=20),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        self.assertEqual(Production.objects.last().grid_meter_reading, 0.75)
        response = factory.post("/input/", data={
            'device_id': 23142,  # Max
            'source_time': self.time_now + timedelta(minutes=21),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 0.5,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 51513,  # Gertrude
            'source_time': self.time_now + timedelta(minutes=25),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 1,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        self.assertAlmostEqual(Consumption.objects.filter(consumer__id=2).last().meter_reading, Decimal(0.6))
