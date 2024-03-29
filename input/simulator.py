import json
import pprint
from datetime import datetime, timedelta
from decimal import Decimal
from time import sleep

from base.contracts.models import Rate
from base.data.models import Production, Consumption, Reading
from base.sensors.models import Producer, Consumer, Sensor
from input.input_handlers import InputHandler
from numpy import random
import requests as make_request

MONTH_FACTOR2 = [.25, .25, .5, .5, .75, 1.75, 3, 2, 1.75, .75, .25, .25]
MONTH_FACTOR3 = [0.396, 0.504, 0.8640000000000001, 1.392, 1.548, 1.608, 1.62, 1.3800000000000001, 1.1400000000000001,
                 0.8640000000000001, 0.40800000000000003, 0.28800000000000003]


def sum_to_n(n):
    values = [0.0, n] + list(random.uniform(low=0.0, high=n, size=n - 1))
    values.sort()
    return [values[i + 1] - values[i] for i in range(n)]


def get_array_input():
    return eval(input("Array mit 24 Einträgen eingeben"))


class EnergySimulator:
    HOUR_FACTOR = [0, 0, 0, 0, 0, 0.5, 0.75, 1, 1.5, 2, 2, 2.5, 2.75, 2.75, 2.5, 2, 1.5, 1, 1, .25, 0, 0, 0, 0]
    MONTH_FACTOR = [0.395, 0.503, 0.863, 1.391, 1.547, 1.607, 1.619, 1.379, 1.139, 0.863, 0.407, 0.287]
    # CONS_HOUR_FACTOR = [1, 0.75, 0.5, 0.25, 0.25, 0.5, 1, 1, 1.5, 1.25, 1, 0.75, 0.75, 0.75, 0.75, 0.75, 1, 1.25, 1.5,
    #                     1.5, 1.75, 1.75, 1.5, 1]
    make_request.packages.urllib3.util.connection.HAS_IPV6 = False
    session = make_request.session()
    daily_production_boost = {'date': "", 'boost': 0}

    def __init__(self, producer_id, start_datetime=None, network_requests=True, with_offset=False,
                 custom_consumption_pattern=False):
        """
        Create a Simulator Instance
        :param producer_id: set the producer which you want to simulate the production and consumption of its consumers
        :param start_datetime: datetime from which the simulation starts
        :param network_requests: set whether simulated requests should be send over network or handled by intern
        InputHandler instance
        :param with_offset: set whether requests should come at different times or all at the same
        :param custom_consumption_pattern: set whether consumption pattern should be auto generated or set manually
        """
        producer = Producer.objects.get(id=producer_id)
        if start_datetime:
            self.timestamp = start_datetime
        else:
            try:
                self.timestamp = Sensor.objects.get(producer__id=producer_id).reading_set.last().time
            except:
                self.timestamp = producer.production_set.last().time + timedelta(minutes=15)
        consumers = []
        max_offset = 15
        if not with_offset:
            max_offset = 0
        consumption_pattern = lambda: sum_to_n(24)
        if custom_consumption_pattern:
            consumption_pattern = lambda: get_array_input()
        for consumer in producer.consumer_set.all():
            consumers.append({'id': consumer.id, 'mean_consumption': float(
                input(f"Jahresdurchscnittsverbrauch von Wohnung:{consumer.name}")),
                              'offset': timedelta(minutes=random.uniform(0, max_offset)),
                              'hour_factors': consumption_pattern()})
        self.consumers = consumers
        self.producer = {'id': producer_id,
                         'mean_production': float(input(f"Jahresdurchscnittsproduktion von PV:{producer.name}")),
                         'production_offset': timedelta(minutes=random.uniform(0, max_offset)),
                         'grid_offset': timedelta(minutes=random.uniform(0, max_offset))}
        self.requests = []
        self.network_requests = network_requests
        self.ih = InputHandler()

    @staticmethod
    def simulate_all():
        producers = Producer.objects.all()
        factories = []
        for producer in producers:
            sim = EnergySimulator(producer.id)
            sim.simulate_until(datetime.now())

    def next(self):
        """
        simulate the next 15 minutes and send all requests out
        :return:
        """
        producer = Producer.objects.get(id=self.producer['id'])
        new_production = self._simulate_production()
        # new production meter is old meter + simulated production
        new_production_meter = new_production + producer.production_set.last().production_meter_reading
        self._create_request(producer.production_sensor, new_production_meter, self.producer['production_offset'])

        total_consumption = 0
        for consumer in self.consumers:
            consumer_instance = Consumer.objects.get(id=consumer['id'])
            new_consumption = self._simulate_consumption(consumer)
            total_consumption += new_consumption
            new_consumption_meter = new_consumption + consumer_instance.consumption_set.last().meter_reading
            self._create_request(consumer_instance.sensor, new_consumption_meter, consumer['offset'])
        new_grid_feed_in = self._simulate_grid_feed_in(new_production, total_consumption)
        # new grid meter is old meter + simulated grid_feed_in
        new_grid_meter = producer.production_set.last().grid_meter_reading + new_grid_feed_in
        self._create_request(producer.grid_sensor, new_grid_meter, self.producer['grid_offset'])
        self._send_requests()
        self.timestamp += timedelta(minutes=15)

    def simulate_until(self, end_date=None):
        """
        Simulates Input until the given end_date.
        !!! ~1-2min per simulated day!!!
        :param end_date: date to which the simulation will run(default= until the time of funtion call)
        :return:
        """
        if not end_date:
            end_date = datetime.now()
        st = datetime.now()
        self.setup()
        while self.timestamp < end_date:
            self.next()
        et = datetime.now()
        print(et - st)

    def setup(self):
        """
        sets up first consumptions and production
        :return:
        """
        producer = Producer.objects.get(id=self.producer['id'])
        if not producer.production_set.first():
            time = datetime.strptime(str(self.timestamp - timedelta(minutes=15)),
                                     '%Y-%m-%d %H:%M:%S.%f').isoformat(' ', 'seconds')
            production = Production.objects.create(time=time, produced=0, used=0,
                                                   production_meter_reading=0, grid_meter_reading=0, producer=producer,
                                                   grid_feed_in=0)
            for consumer in producer.consumer_set.all():
                consumption = Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0,
                                                         consumer=consumer, time=time,
                                                         production=production, price=0, rate=Rate.objects.first(),
                                                         grid_price=0, reduced_price=0, saved=0, consumption=0)

    def _simulate_production(self):
        daily_boost = self.daily_production_boost
        timestamp = self.timestamp
        current_month = timestamp.month
        current_hour = timestamp.hour

        # To make simulations more different, there is a small chance that the production is boosted or worsen
        # (like sunny days and rainy days), at best double the mean_production at worst 0
        hour_factor = self.HOUR_FACTOR[current_hour]
        if not daily_boost['date'] == timestamp.date():
            if random.random() < 0.2 / (24 * 4): # to make possibility to 20% over all boosts of one day
                daily_boost = {'date': timestamp.date(), 'boost': random.uniform(0, 2)}
            else:
                daily_boost['boost'] = 0
        if daily_boost['date'] == timestamp.date():
            hour_factor *= daily_boost['boost']

        if self.HOUR_FACTOR[current_hour] > 0:
            # if we take the average and divide it like below we have a production we can add every 15min for a year
            # to exactly get the year average. In some hours and month more is produced than in others. That's why
            # the 15-min average is multiplied by a set factor and possibly by the boost factor above.
            mean = self.producer['mean_production'] / ( 365 * 24 * 4 ) * self.MONTH_FACTOR[
                current_month - 1] * hour_factor
            # The outcome is then taken as the mean for a normal distribution, to make it non-deterministic
            production = random.normal(mean, mean * 0.1)
        # So that no negative production is possible
        if self.HOUR_FACTOR[current_hour] == 0 or production < 0:
            production = 0
        self.daily_production_boost = daily_boost

        return Decimal(production)

    @staticmethod
    def _simulate_grid_feed_in(production, consumption):
        """
        the max grid_feed_in is all that was produced.
        If more or equal was consumed than produced:
            the grid_feed_in can be 0, because all produced power could have been used directly.
        Else:
            grid_feed_in has to be atleast the difference of produced and consumed, so that all power that could not
            have been used directly is registered in grid_feed_in

        :param production: produced in this iteration
        :param consumption: consumed in this iteration
        :return: fed in, in this iteration
        """
        if production > 0:
            minimum = 0
            maximum = production
            if consumption < production:
                minimum = production - consumption
            res = Decimal(random.uniform(minimum, maximum))
            return res
        else:
            return 0

    def _simulate_consumption(self, consumer):
        timestamp = self.timestamp
        current_hour = timestamp.hour
        hour_factor = consumer['hour_factors'][current_hour]

        # To make simulations more different from each other
        if random.random() < 0.1:
            hour_factor *= random.uniform(0, 2)
        # if we take the average and divide it like below we have a consumption we can add every 15min for a year to
        # exactly get the year average. In some hours more is consumed than in others. That's why the 15-min average
        # is multiplied by a set factor and possibly by the boost factor above.
        if consumer['hour_factors'][current_hour] > 0:
            mean = consumer['mean_consumption'] / 365 / 24 / 4 * hour_factor
            # The outcome is then taken as the mean for a normal distribution, to make it non-deterministic
            consumption = random.normal(mean, mean * 0.2)
        # no negative consumption possible
        if consumer['hour_factors'][current_hour] == 0 or consumption < 0:
            consumption = 0

        return Decimal(consumption)

    def _create_request(self, sensor, energy, offset):
        """
        Creates a request and add it to the request queue
        :param sensor: sensor of consumer/producer
        :param energy: meter of consumption/production/grid_feed_in
        :param offset: how much after the timestamp the request should be send
        :return:
        """
        request_data = {
            'device_id': sensor.device_id,
            'source_time': str(self.timestamp + offset),
            'parsed': {
                'Bezug_Gesamt_kWh': 0,
                'Lieferung_Gesamt_kWh': 0,
                'Leistung_Summe_W': 0
            }}
        if sensor.type in ['PM', 'GM']:
            request_data['parsed']['Lieferung_Gesamt_kWh'] = energy
        else:
            request_data['parsed']['Bezug_Gesamt_kWh'] = energy
        self.requests.append(request_data)

    def _send_requests(self):
        requests = sorted(self.requests, key=lambda x: x['source_time'])
        for request in requests:
            if self.network_requests:
                self.session.post('http://localhost:8000/input/', json=request)
            else:
                self.ih.request = {'data': request}
                self.ih.handle_input()
        self.requests = []

    @staticmethod
    def _delete_data(producer_id=False):
        if not producer_id:
            reading_set = Reading.objects.all()
            consumption_set = Consumption.objects.all()
            production_set = Production.objects.all()
            producer_set = Producer.objects.all()
            consumer_set = Consumer.objects.all()
        else:
            pass
        reading_set.delete()
        consumption_set.delete()
        production_set.delete()
        for p in producer_set:
            p.last_grid_reading = None
            p.last_production_reading = None
            p.save()
        for c in consumer_set:
            c.last_reading = None
            c.save()
