""" from django.test import TestCase, Client
from django.urls import reverse
from energy2_backend.urls import *
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from decimal import Decimal
from output.views import output_view, get_productions_and_aggregations, get_consumptions_and_aggregations
from pprint import pprint

producer_dump = {"name": "T", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
consumer_dump = {"name": "t", "email": "t@t.de", "phone": "0004123420", }

# Create your tests here.
class OutputTest(TestCase):
    time_now = datetime.now()
    time_now = datetime(day=12, month=1, year=2023, hour=10, minute=0) # time_now = 10:00

    '''Initial setup of objects'''
    def setUp(self) -> None:
        time_now = self.time_now

        # Create production and grid sensors, producer object and production object
        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        print(Sensor.objects.all())
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
        
    

    def test_get_consumptions_and_aggregations(self):
        time_now = self.time_now
        consumer = Consumer.objects.first()
        start_date = time_now
        end_date = time_now + timedelta(days=1)

        print(get_consumptions_and_aggregations(consumer, start_date, end_date)) """


from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from base.data.models import Production, Consumption
from base.data.serializers import ProductionSerializer, ConsumptionSerializer
from base.sensors.models import Producer, Consumer

class OutputTest(TestCase):
    def setUp(self):
        # create a consumer and some consumptions
        self.consumer = Consumer.objects.create(name='Test Consumer')
        self.consumption1 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=5), meter_reading=100, consumption=50, self_consumption=30, price=100, reduced_price=80, saved=20)
        self.consumption2 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=3), meter_reading=150, consumption=40, self_consumption=20, price=80, reduced_price=60, saved=20)
        self.consumption3 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=1), meter_reading=180, consumption=30, self_consumption=10, price=60, reduced_price=50, saved=10)

    def test_get_consumptions_and_aggregations(self):
        # make a GET request to the view
        url = reverse('consumptions')
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        response = self.client.get(url, {'consumer': self.consumer.id, 'start_date': start_date, 'end_date': end_date})
        
        # check that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # check that the response contains the expected data
        expected_data = {
            'id': self.consumer.id,
            'consumptions': ConsumptionSerializer([self.consumption1, self.consumption2, self.consumption3], many=True, context={'request': response.wsgi_request}).data,
            'total_consumption': 70,
            'total_self_consumption': 60,
            'total_grid_consumption': 10,
            'total_price': 240,
            'total_reduced_price': 190,
            'total_grid_price': 50,
            'total_saved': 40
        }
        self.assertEqual(response.data, expected_data)