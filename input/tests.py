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
class InputTest(TestCase):
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
    
    '''First test help functions'''
    
    # Test _interpolate function
    def test_interpolate(self):
        time_now = self.time_now
        ih = InputHandler(request=None, producer=Producer.objects.first())
        producer = Producer.objects.first()
        print(producer.production_set.last())
        last_production = producer.production_set.last() # last_production.time = time_now = 10:00 

        # Create exemplary data
        new_production_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=15),  # 10:15
                                                        sensor=Producer.objects.first().production_sensor)
        new_grid_reading = Reading.objects.create(energy=Decimal(1.5), power=0, time=time_now + timedelta(minutes=20), # 10:20
                                                  sensor=Producer.objects.first().grid_sensor)
        left = {'value': last_production.grid_meter_reading, 'time': last_production.time}
        right = {'value': new_grid_reading.energy, 'time': new_grid_reading.time}
        target_time = new_production_reading.time # 10:15
        
        # Interpolate value of grid reading (energy = 1.5) from 10:20 to target_time of production reading at 10:15.
        # Here: length = 20 minutes, target_time at 15 minutes, i.e. 3/4 of difference. 
        # Hence, interpolated grid_reading value is 1.5 * (3/4) = 1.125
        self.assertEqual(ih._interpolate(left, right, target_time), 1.125)


    # Test _divide_production_among_consumption function and _assign_rate_and_price_to_consumption function
    def test_divide_production_among_consumption_assign_rate_and_price_to_consumption(self):
        time_now = self.time_now
        production = Production.objects.create(time=time_now + timedelta(minutes=15), produced=0.2, used=0.15,
                                                   production_meter_reading=0.2, grid_feed_in=0.05,
                                                   grid_meter_reading=0.05, producer=Producer.objects.first())
        consumer = Consumer.objects.get(id=2)
        consumption = Consumption.objects.get(id=2)
        rate = Rate.objects.first()

        ih = InputHandler(request=None, producer=Producer.objects.first())
        ih.production=production

        consumptions = {1:{'meter_reading':Decimal(0.3), 'consumption':Decimal(0.3), 'last_consumption':consumption, 
                        'time':time_now + timedelta(minutes=15), 'consumer':consumer, 'production':production}}

        # Execute the _divide_production_among_consumption function with the consumptions object
        # The _assign_rate_and_price_to_consumption function is executed within the _divide_production_among_consumption function
        ih._divide_production_among_consumption(consumptions)

        self.assertAlmostEqual(consumptions[1]['self_consumption'], Decimal('0.14999999'))
        self.assertAlmostEqual(consumptions[1]['grid_consumption'], Decimal('0.14999999'))
        self.assertEqual(consumptions[1]['rate'], rate)
        self.assertAlmostEqual(consumptions[1]['reduced_price'], Decimal('5.24999999'))
        self.assertAlmostEqual(consumptions[1]['grid_price'], Decimal('5.99999999'))
        self.assertAlmostEqual(consumptions[1]['price'], Decimal('11.24999999'))
        self.assertAlmostEqual(consumptions[1]['saved'], Decimal('0.74999999'))


    '''Then test main functions'''

    '''4 tests for _check_for_new_productions() and _create_new_production()'''

    # (1) Regular cases
    def test_productions_regular(self):
        time_now = self.time_now
        ih = InputHandler(request=None, producer=Producer.objects.first())

        new_production_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=15),
                                                        sensor=Producer.objects.first().production_sensor)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), False)
        new_grid_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=20),
                                                  sensor=Producer.objects.first().grid_sensor)
        print(Producer.objects.get(id=1).last_production_reading)
        print(Producer.objects.get(id=1).last_grid_reading)
        self.assertEqual(ih._check_for_new_production(), False) # a reading from both production and grid sensor now exists, but...
        ih.producer.refresh_from_db() # refreshing the producer with the new reading from the database is necessary
        self.assertEqual(ih._check_for_new_production(), True)
        
        ih._create_new_production()
        self.assertEqual(Production.objects.last().time, datetime(day=12, month=1, year=2023, hour=10, minute=15))
        self.assertEqual(Production.objects.last().produced, 1)
        # grid_feed_in = interpolated_grid_meter_reading - last_production.grid_meter_reading = 0.75
        # new_production_data['used'] = new_production_data['produced'] - grid_feed_in = 1 - 0.75 = 0.25
        self.assertEqual(Production.objects.last().used, 0.25)
        
        # Try with new readings
        new_production_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=30),
                                                        sensor=Producer.objects.first().production_sensor)
        new_grid_reading = Reading.objects.create(energy=1, power=0, time=time_now + timedelta(minutes=35),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        print(Reading.objects.all())
        self.assertEqual(ih._check_for_new_production(), True)
        
        ih._create_new_production()
        # For both sensors the readings are the same as in the previous production (energy = 1).
        # Hence, nothing was produced or used.
        self.assertEqual(Production.objects.last().produced, 0)
        self.assertEqual(Production.objects.last().used, 0)

    # (2) Edge case: Try with different order of readings, i.e. when grid input comes before production input
    def test_productions_edge_order(self):
        time_now = self.time_now
        ih = InputHandler(request=None, producer=Producer.objects.first())

        new_grid_reading = Reading.objects.create(energy=Decimal(0.8), power=0, time=time_now + timedelta(minutes=39),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), False)

        new_production_reading = Reading.objects.create(energy=Decimal(1.2), power=0, time=time_now + timedelta(minutes=46),
                                                        sensor=Producer.objects.first().production_sensor)
        self.assertEqual(ih._check_for_new_production(), False)
        ih.producer.refresh_from_db()
        # Still False because grid_reading to be considered must be newer than production_reading. So we keep waiting...
        self.assertEqual(ih._check_for_new_production(), False)

        new_grid_reading = Reading.objects.create(energy=Decimal(0.9), power=0, time=time_now + timedelta(minutes=48),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        self.assertEqual(ih._check_for_new_production(), True) # ... now this is the case

        ih._create_new_production()
        self.assertEqual(Production.objects.last().time, datetime(day=12, month=1, year=2023, hour=10, minute=46))
        self.assertEqual(Production.objects.last().produced, 1.2)
        self.assertEqual(Production.objects.last().production_meter_reading, 1.2)
        self.assertEqual(Production.objects.last().grid_feed_in, 0.8625)
        self.assertEqual(Production.objects.last().used, 0.3375)
        self.assertEqual(Production.objects.last().grid_meter_reading, 0.8625)

    # (3) Edge case: if no production input for a long time (e.g. because communication module of sensor is broken and cannot deliver data)
    # --> spins in while loop in handle_input as long as there is no production data
    def test_productions_edge_noProduction(self):
        time_now = self.time_now
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)

        # Simulates incoming input from which readings can be created
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
        self.assertEqual(Producer.production_set.last().time, self.time_now + timedelta(minutes=15))
        self.assertEqual(Production.objects.last().grid_meter_reading, 0.75)

        response = factory.post("/input/", data={
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=74),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1.86,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        response = factory.post("/input/", data={
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=102), # 10:00 + 102 minutes = 11:42
            'parsed': {
                'Lieferung_Gesamt_kWh': 2.1,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        # No new production could have been created, i.e. the time is still the same as the first production
        self.assertEqual(Producer.production_set.last().time, self.time_now + timedelta(minutes=15))

        # Imagine in the meantime several more grid data inputs have come and now finally...
        # ... the sensor could be fixed and is delivering input data again
        response = factory.post("/input/", data={
            'device_id': 123123,  # PV
            'source_time': self.time_now + timedelta(minutes=391), # 16:31
            'parsed': {
                'Lieferung_Gesamt_kWh': 14.68,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        # Now we need to wait for one more grid input
        response = factory.post("/input/", data={
            'device_id': 46454,  # Grid
            'source_time': self.time_now + timedelta(minutes=394), # 16:34
            'parsed': {
                'Lieferung_Gesamt_kWh': 6.94,
                'Bezug_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }
        }, format='json')
        self.assertEqual(Production.objects.last().time, self.time_now + timedelta(minutes=391))
        self.assertEqual(Production.objects.last().produced, 13.68)
        self.assertEqual(Production.objects.last().production_meter_reading, 14.68)
        self.assertEqual(Production.objects.last().grid_feed_in, round(Decimal(6.1371573604),4))
        self.assertEqual(Production.objects.last().used, round(Decimal(7.5428426396),4))
        self.assertEqual(Production.objects.last().grid_meter_reading, round(Decimal(6.8871573604),4))

    # (4) Edge case: if no grid input for a long time
    def test_productions_edge_noGrid(self):
        time_now = self.time_now

    '''x tests for _check_for_new_consumption() and _create_consumptions()'''

    # (1) Regular case
    # Test _check_for_new_consumption() and _create_consumptions() functions
    def test_create_consumptions_regular(self):
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
        self.assertEqual(ih._check_for_new_consumption(), True) # now one reading for each consumer exists, so consumption can be created
        
        new_production_reading = Reading.objects.create(energy=0.3, power=0, time=time_now + timedelta(minutes=30),
                                                        sensor=Producer.objects.first().production_sensor)
        new_grid_reading = Reading.objects.create(energy=0.1, power=0, time=time_now + timedelta(minutes=35),
                                                  sensor=Producer.objects.first().grid_sensor)
        ih.producer.refresh_from_db()
        ih._create_new_production()
        ih._create_consumptions()

        self.assertEqual(Consumption.objects.last().time, datetime(day=12, month=1, year=2023, hour=10, minute=15))
        self.assertEqual(Consumption.objects.last().consumption, round(Decimal(0.3), 4))
        self.assertEqual(Consumption.objects.last().grid_consumption, round(Decimal(0.225), 4))
        self.assertEqual(Consumption.objects.last().grid_price, round(Decimal(9.0), 4))
        self.assertEqual(Consumption.objects.last().meter_reading, round(Decimal(0.3), 4))
        self.assertEqual(Consumption.objects.last().price, round(Decimal(11.625), 4))
        self.assertEqual(Consumption.objects.last().reduced_price, round(Decimal(2.625), 4))
        self.assertEqual(Consumption.objects.last().saved, round(Decimal(0.375), 4))
        self.assertEqual(Consumption.objects.last().self_consumption, round(Decimal(0.075), 4))

    # (2) Edge case: no consumption reading for a long time
    # Test _check_for_new_consumption() and _create_consumptions() functions
    def test_create_consumptions_edge(self):
        time_now = self.time_now
        user = User.objects.first()
        factory = APIClient(enforce_csrf_checks=False)

        response = factory.post("/input/", data={
            'device_id': 51513,  # Gertrude
            'source_time': self.time_now + timedelta(minutes=25),
            'parsed': {
                'Lieferung_Gesamt_kWh': 1,
                'Bezug_Gesamt_kWh': 1,
                'Leistung_Summe_W': 0
            }
        }, format='json')


    '''Finally test whole input handler'''

    # Test _handle_input function
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
