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


""" from django.test import TestCase
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
        self.assertEqual(response.data, expected_data) """





""" from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from energy2_backend.urls import *
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from decimal import Decimal
#from output.views import output_view, get_productions_and_aggregations, get_consumptions_and_aggregations
from pprint import pprint


class OutputTest(TestCase):
    time_now = datetime.now()
    time_now = datetime(day=12, month=1, year=2023, hour=10, minute=0) # time_now = 10:00
    
    def setUp(self):
        time_now = self.time_now
        producer_dump = {"name": "T", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
        consumer_dump = {"name": "t", "email": "t@t.de", "phone": "0004123420", }
        # Create production and grid sensors, producer object and production object
        pm = Sensor.objects.create(device_id=123123, type="PM")
        gm = Sensor.objects.create(device_id=46454, type="GM")
        print(Sensor.objects.all())
        prod = Producer.objects.create(**producer_dump, production_sensor=pm, grid_sensor=gm)
        prdctn = Production.objects.create(time=time_now, produced=0, used=0, production_meter_reading=0,
                                           grid_meter_reading=0, producer=prod, grid_feed_in=0)

        # Create rate
        rate = Rate.objects.create(price=40, reduced_price=35)

        # create a consumer and some consumptions

        # Create first user and his consumption sensor
        u1 = User.objects.create(username="max", password="sakhdk124")
        s1 = Sensor.objects.create(device_id=23142, type="CM")
        con1 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s1, user=u1)
        con1.rates.add(rate)
        con1.save()
        #self.consumption1 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=5), meter_reading=100, consumption=50, self_consumption=30, price=100, reduced_price=80, saved=20)
        self.cons1 = Consumption.objects.create(self_consumption=30, grid_consumption=0, meter_reading=100, consumer=con1,
                                           time=time_now, production=prdctn, price=100, rate=rate, grid_price=0,
                                           reduced_price=80, saved=20, consumption=50)

        # Create second user and her consumption sensor
        u2 = User.objects.create(username="gertrude", password="sakhdk124")
        s2 = Sensor.objects.create(device_id=51513, type="CM")
        con2 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s2, user=u2)
        con2.rates.add(rate)
        con2.save()
        #self.consumption2 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=3), meter_reading=150, consumption=40, self_consumption=20, price=80, reduced_price=60, saved=20)
        self.cons2 = Consumption.objects.create(self_consumption=20, grid_consumption=0, meter_reading=150, consumer=con2,
                                           time=time_now, production=prdctn, price=80, rate=rate, grid_price=0,
                                           reduced_price=60, saved=20, consumption=40)
        
        # Create second user and her consumption sensor
        u3 = User.objects.create(username="solarsören", password="sakhdk124")
        s3 = Sensor.objects.create(device_id=51515, type="CM")
        con3 = Consumer.objects.create(**consumer_dump, producer=prod, sensor=s3, user=u3)
        con3.rates.add(rate)
        con3.save()
        #self.consumption3 = Consumption.objects.create(consumer=self.consumer, time=timezone.now() - timedelta(days=1), meter_reading=180, consumption=30, self_consumption=10, price=60, reduced_price=50, saved=10)
        self.cons3 = Consumption.objects.create(self_consumption=10, grid_consumption=0, meter_reading=180, consumer=con2,
                                           time=time_now, production=prdctn, price=60, rate=rate, grid_price=0,
                                           reduced_price=50, saved=10, consumption=30)
        
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
            'consumptions': ConsumptionSerializer([self.cons1, self.cons2, self.cons3], many=True, context={'request': response.wsgi_request}).data,
            'total_consumption': 70,
            'total_self_consumption': 60,
            'total_grid_consumption': 10,
            'total_price': 240,
            'total_reduced_price': 190,
            'total_grid_price': 50,
            'total_saved': 40
        }
        self.assertEqual(response.data, expected_data) """




import json
from pprint import pprint

from django.test import TestCase
from energy2_backend.urls import *
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from input.views import InputHandler
from decimal import Decimal

# House 1
producer1_dump = {"name": "P1", "street": "t", "zip_code": "t", "city": "2", "peak_power": 1}
consumer1_dump = {"name": "max", "email": "m@t.de", "phone": "0004123420", }
consumer2_dump = {"name": "gertrude", "email": "g@t.de", "phone": "0004123421", }

# House 2
producer2_dump = {"name": "P2", "street": "a", "zip_code": "a", "city": "3", "peak_power": 1}
consumer3_dump = {"name": "angela", "email": "a@t.de", "phone": "0004123422", }
consumer4_dump = {"name": "olaf", "email": "o@t.de", "phone": "0004123423", }
consumer5_dump = {"name": "annalena", "email": "an@t.de", "phone": "0004123424", }


# Create your tests here.
class OutputTest(TestCase):
    time_now = datetime.now()

    # Initial set up of sensors, producers, consumers and as well as subsequent set up of productions and consumptions for each
    def setUp(self) -> None:
        time_now = self.time_now

        '''Initial set up of sensors, producers and consumers'''

        '''House 1'''

        # Create production and grid sensors, producer object and production object
        pm1 = Sensor.objects.create(device_id=123123, type="PM")
        gm1 = Sensor.objects.create(device_id=46454, type="GM")
        prod1 = Producer.objects.create(**producer1_dump, production_sensor=pm1, grid_sensor=gm1)
        prdctn1 = Production.objects.create(time=time_now, produced=0, used=0, production_meter_reading=0,
                                            grid_meter_reading=0, producer=prod1, grid_feed_in=0)

        # Create rate
        rate = Rate.objects.create(price=40, reduced_price=35)

        # Create first user and his consumption sensor
        u1 = User.objects.create(username="max", password="sakhdk124")
        cm1 = Sensor.objects.create(device_id=23142, type="CM")
        con1 = Consumer.objects.create(**consumer1_dump, producer=prod1, sensor=cm1, user=u1)
        con1.rates.add(rate)
        con1.save()
        cons1 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con1,
                                           time=time_now, production=prdctn1, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        # Create second user and her consumption sensor
        u2 = User.objects.create(username="gertrude", password="sakhdk124")
        cm2 = Sensor.objects.create(device_id=51513, type="CM")
        con2 = Consumer.objects.create(**consumer2_dump, producer=prod1, sensor=cm2, user=u2)
        con2.rates.add(rate)
        con2.save()
        cons2 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con2,
                                           time=time_now, production=prdctn1, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        '''House 2'''

        # Create production and grid sensors, producer object and production object
        pm2 = Sensor.objects.create(device_id=789789, type="PM")
        gm2 = Sensor.objects.create(device_id=56789, type="GM")
        prod2 = Producer.objects.create(**producer2_dump, production_sensor=pm2, grid_sensor=gm2)
        prdctn2 = Production.objects.create(time=time_now, produced=0, used=0, production_meter_reading=0,
                                            grid_meter_reading=0, producer=prod2, grid_feed_in=0)

        # Same rate as house 1
        # rate = Rate.objects.filter(price=40, reduced_price=35).first()

        # Create third user and her consumption sensor
        u3 = User.objects.create(username="angela", password="sakhdk124")
        cm3 = Sensor.objects.create(device_id=33737, type="CM")
        con3 = Consumer.objects.create(**consumer3_dump, producer=prod2, sensor=cm3, user=u3)
        con3.rates.add(rate)
        con3.save()
        cons3 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con3,
                                           time=time_now, production=prdctn2, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        # Create fourth user and his consumption sensor
        u4 = User.objects.create(username="olaf", password="sakhdk124")
        cm4 = Sensor.objects.create(device_id=65432, type="CM")
        con4 = Consumer.objects.create(**consumer4_dump, producer=prod2, sensor=cm4, user=u4)
        con4.rates.add(rate)
        con4.save()
        cons4 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con4,
                                           time=time_now, production=prdctn2, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        # Create fifth user and his consumption sensor
        u5 = User.objects.create(username="annalena", password="sakhdk124")
        cm5 = Sensor.objects.create(device_id=19191, type="CM")
        con5 = Consumer.objects.create(**consumer5_dump, producer=prod2, sensor=cm5, user=u5)
        con5.rates.add(rate)
        con5.save()
        cons5 = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0, consumer=con5,
                                           time=time_now, production=prdctn2, price=0, rate=rate, grid_price=0,
                                           reduced_price=0, saved=0, consumption=0)

        '''Admin'''
        admin = User.objects.create(username="admin", password="13ß9zt5321", is_staff=True)

        '''Set up subsequent productions and consumptions for each producer and consumer to use in tests'''

        # House 1
        new_production1 = Production.objects.create(time=time_now + timedelta(minutes=15), produced=1, used=1,
                                                    production_meter_reading=1, grid_meter_reading=0, producer=prod1,
                                                    grid_feed_in=0)
        max_consumption1 = Consumption.objects.create(time=time_now + timedelta(minutes=15), self_consumption=0.125,
                                                      grid_consumption=1.5, consumption=1.625, meter_reading=1.625,
                                                      rate=rate,
                                                      reduced_price=Decimal(4.375), grid_price=Decimal(60),
                                                      price=Decimal(64.375),
                                                      saved=Decimal(0.625), production=new_production1, consumer=con1)
        gertrude_consumption1 = Consumption.objects.create(time=time_now + timedelta(minutes=15),
                                                           self_consumption=0.125,
                                                           grid_consumption=2, consumption=2.125, meter_reading=2.125,
                                                           rate=rate,
                                                           reduced_price=Decimal(4.375), grid_price=Decimal(80),
                                                           price=Decimal(84.375),
                                                           saved=Decimal(0.625), production=new_production1,
                                                           consumer=con2)
        new_production2 = Production.objects.create(time=time_now + timedelta(minutes=32), produced=1.2, used=1,
                                                    production_meter_reading=2.2, grid_meter_reading=0.2,
                                                    producer=prod1, grid_feed_in=0.2)
        max_consumption2 = Consumption.objects.create(time=time_now + timedelta(minutes=32), self_consumption=1,
                                                      grid_consumption=0, consumption=1, meter_reading=2.625, rate=rate,
                                                      reduced_price=Decimal(35), grid_price=Decimal(0),
                                                      price=Decimal(35),
                                                      saved=Decimal(5), production=new_production2, consumer=con1)
        gertrude_consumption2 = Consumption.objects.create(time=time_now + timedelta(minutes=32), self_consumption=0,
                                                           grid_consumption=0, consumption=0, meter_reading=2.125,
                                                           rate=rate,
                                                           reduced_price=0, grid_price=0, price=0,
                                                           saved=0, production=new_production2, consumer=con2)

        # House 2
        new_production3 = Production.objects.create(time=time_now + timedelta(minutes=15), produced=2, used=1.8,
                                                    production_meter_reading=2, grid_meter_reading=0.2, producer=prod2,
                                                    grid_feed_in=0.2)
        angela_consumption = Consumption.objects.create(time=time_now + timedelta(minutes=15), self_consumption=0.4,
                                                        grid_consumption=0, consumption=0.4, meter_reading=0.4,
                                                        rate=rate,
                                                        reduced_price=Decimal(14), grid_price=0, price=Decimal(14),
                                                        saved=Decimal(2), production=new_production3, consumer=con3)
        olaf_consumption = Consumption.objects.create(time=time_now + timedelta(minutes=15), self_consumption=0.6,
                                                      grid_consumption=0, consumption=0.6, meter_reading=0.6, rate=rate,
                                                      reduced_price=Decimal(21), grid_price=Decimal(0),
                                                      price=Decimal(21),
                                                      saved=Decimal(3), production=new_production3, consumer=con4)
        annalena_consumption = Consumption.objects.create(time=time_now + timedelta(minutes=15), self_consumption=0.8,
                                                          grid_consumption=0, consumption=0.8, meter_reading=0.8,
                                                          rate=rate,
                                                          reduced_price=Decimal(28), grid_price=Decimal(0),
                                                          price=Decimal(28),
                                                          saved=Decimal(4), production=new_production3, consumer=con5)

    # Test output when neither producer_id nor consumer_id is given, i.e. test aggregated production & consumption over all producers & consumers
    # Ref.: line 63 in output/views.py
    def test_all_productions(self):
        print(Production.objects.all())
        user = User.objects.filter(id=6).first()  # admin
        c = APIClient(enforce_csrf_checks=False)
        c.force_login(user=user)
        response = c.get("/output/?")  # producer_id = 1
        print(response)
        
        self.assertAlmostEqual(response.data['producers_total_production'], Decimal(4.2))
        self.assertAlmostEqual(response.data['producers_total_used'], Decimal(3.8))
        self.assertAlmostEqual(response.data['producers_total_revenue'], Decimal(246.75))
        self.assertAlmostEqual(response.data['producers_total_consumption'], Decimal(6.55))
        self.assertAlmostEqual(response.data['producers_total_saved'], Decimal(15.25))

    # Test output when only producer_id is given, i.e. test _get_productions_and_aggregations() function
    def test_production(self):
        user = User.objects.filter(id=6).first()  # admin
        c = APIClient(enforce_csrf_checks=False)
        c.force_login(user=user)
        response = c.get("/output/?producer_id=1&")  # producer_id = 1
        print(response.data)

        self.assertAlmostEqual(response.data['total_production'], Decimal(2.2))
        self.assertAlmostEqual(response.data['total_used'], 2)
        self.assertAlmostEqual(response.data['consumers_total_revenue'], Decimal(183.75))
        self.assertAlmostEqual(response.data['consumers_total_consumption'], Decimal(4.75))
        self.assertAlmostEqual(response.data['consumers_total_saved'], Decimal(6.25))


    # Test output when only consumer_id is given, i.e. test the consumer output
    def test_consumption(self):
        user = User.objects.filter(id=6).first()  # admin
        c = APIClient(enforce_csrf_checks=False)
        c.force_login(user=user)
        response = c.get("/output/?consumer_id=1&")  # consumer_id = 1

        self.assertEqual(response.data['total_consumption'], Decimal('2.6250000000'))
        self.assertEqual(response.data['total_self_consumption'], Decimal('1.125'))
        self.assertEqual(response.data['total_grid_consumption'], Decimal('1.5000000000'))
        self.assertEqual(response.data['total_price'], Decimal('99.375'))
        self.assertEqual(response.data['total_reduced_price'], Decimal('39.375'))
        self.assertEqual(response.data['total_grid_price'], Decimal('60.000'))
        self.assertEqual(response.data['total_saved'], Decimal('5.625'))