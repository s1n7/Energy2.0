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
        expected_content = {'producers': {
            'P1': {'consumers': {'gertrude': {'consumptions': ConsumptionSerializer(data=Consumption.objects.filter(consumer__name='gertrude')).serialized_data,
                                              'id': 2,
                                              'total_consumption': Decimal('2.1250000000'),
                                              'total_grid_consumption': Decimal('2.0000000000'),
                                              'total_grid_price': Decimal('80.000'),
                                              'total_price': Decimal('84.375'),
                                              'total_reduced_price': Decimal('4.375'),
                                              'total_saved': Decimal('0.625'),
                                              'total_self_consumption': Decimal('0.125')},
                                 'max': {'consumptions': Consumption.objects.filter(consumer__name='max'),
                                         'id': 1,
                                         'total_consumption': Decimal('2.6250000000'),
                                         'total_grid_consumption': Decimal(
                                             '1.5000000000'),
                                         'total_grid_price': Decimal('60.000'),
                                         'total_price': Decimal('99.375'),
                                         'total_reduced_price': Decimal('39.375'),
                                         'total_saved': Decimal('5.625'),
                                         'total_self_consumption': Decimal('1.125')}},
                   'consumers_total_consumption': Decimal('4.7500000000'),
                   'consumers_total_revenue': Decimal('183.750'),
                   'consumers_total_saved': Decimal('6.250'),
                   'productions': Production.objects.filter(producer__name="P1"),
                   'total_production': Decimal('2.2000000000'),
                   'total_used': Decimal('2.0000000000')},
            'P2': {'consumers': {'angela': {'consumptions': Consumption.objects.filter(consumer__name='angela'),
                                            'id': 3,
                                            'total_consumption': Decimal('0.4000000000'),
                                            'total_grid_consumption': Decimal('0E-15'),
                                            'total_grid_price': Decimal('0'),
                                            'total_price': Decimal('14'),
                                            'total_reduced_price': Decimal('14'),
                                            'total_saved': Decimal('2'),
                                            'total_self_consumption': Decimal(
                                                '0.400000000000000')},
                                 'annalena': {'consumptions': Consumption.objects.filter(consumer__name='annalena'),
                                              'id': 5,
                                              'total_consumption': Decimal(
                                                  '0.8000000000'),
                                              'total_grid_consumption': Decimal('0E-15'),
                                              'total_grid_price': Decimal('0'),
                                              'total_price': Decimal('28'),
                                              'total_reduced_price': Decimal('28'),
                                              'total_saved': Decimal('4'),
                                              'total_self_consumption': Decimal(
                                                  '0.800000000000000')},
                                 'olaf': {'consumptions': Consumption.objects.filter(consumer__name='olaf'),
                                          'id': 4,
                                          'total_consumption': Decimal('0.6000000000'),
                                          'total_grid_consumption': Decimal('0E-15'),
                                          'total_grid_price': Decimal('0'),
                                          'total_price': Decimal('21'),
                                          'total_reduced_price': Decimal('21'),
                                          'total_saved': Decimal('3'),
                                          'total_self_consumption': Decimal(
                                              '0.600000000000000')}},
                   'consumers_total_consumption': Decimal('1.8000000000'),
                   'consumers_total_revenue': Decimal('63'),
                   'consumers_total_saved': Decimal('9'),
                   'productions': Production.objects.filter(producer__name="P2"),
                   'total_production': Decimal('2.0000000000'),
                   'total_used': Decimal('1.8000000000')}},
            'producers_total_consumption': Decimal('6.5500000000'),
            'producers_total_production': Decimal('4.2000000000'),
            'producers_total_revenue': Decimal('246.750'),
            'producers_total_saved': Decimal('15.250'),
            'producers_total_used': Decimal('3.8000000000')}
        print(response.data)
        pprint(json.loads(response.content))
        self.maxDiff = None
        self.assertDictEqual(expected_content, response.data)#json.loads(response.content))

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
