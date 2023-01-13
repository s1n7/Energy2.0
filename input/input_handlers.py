import datetime
from decimal import Decimal
from pprint import pprint

from base.data.models import Reading, Production, Consumption
from base.sensors.models import Sensor
from django.db.models import Q


class InputHandler:

    def __init__(self, request=None, producer=None):
        self.producer = producer
        self.request = request
        self.sensor = None
        self.data = None

    def handle_input(self):
        # if request is none, no reading should be created but check for new possible productions or consumptions
        st = datetime.datetime.now()
        if self.request is not None:
            request = self.request
            device_id = self.request.data['device_id']
            self.data = request.data['parsed']
            self.data['source_time'] = request.data['source_time']
            # from request get device_id and get the according sensor instance
            # TODO: What if no sensor with id exists
            self.sensor = Sensor.objects.get(device_id=device_id)
            sensor = self.sensor
            # Depending on the sensor type the according producer has to be fetched differently
            if sensor.type == "CM":  # Consumption Meter
                self.producer = sensor.consumer.producer
            elif sensor.type == "PM":  # Production Meter
                self.producer = sensor.producer
            elif sensor.type == "GM":  # Grid Meter
                self.producer = sensor.producer_grid
            self._save_input_as_reading()
        # after reading was created we now can check if new productions and/or consumptions are possible to create
        # if self._check_for_new_consumption():
        #     self._create_consumptions()
        if self._check_for_new_production():
            self._create_new_production()
        et = datetime.datetime.now()
        print(et - st)

    def _save_input_as_reading(self):
        """
        If request comes from sensor, a Reading object is created based on the request
        """
        sensor = self.sensor
        data = self.data
        # Depending on the sensor type the data has to be fetched differently
        if sensor.type == "CM":
            energy = data['Bezug_Gesamt_kWh']
        elif sensor.type == "GM":
            energy = data['Lieferung_Gesamt_kWh']
        elif sensor.type == "PM":
            energy = data['Lieferung_Gesamt_kWh']
        # store reading data and create Reading object
        reading_data = {
            'power': data['Leistung_Summe_W'],
            'energy': energy,
            'time': datetime.datetime.strptime(data['source_time'], '%Y-%m-%d %H:%M:%S.%f').isoformat(' ', 'seconds'),
            'sensor': sensor
        }
        reading = Reading(**reading_data)
        reading.save()

    def _check_for_new_consumption(self):
        """
        Checks if new consumptions for the consumers of the given producer can be created.
        This is the case if a Reading exists for every consumer that is the same or younger than the oldest production
        that is has no consumptions assigned yet
        """
        # oldest production of producer that has no consumptions assigned yet
        production = Production.objects.filter(producer=self.producer, consumption__isnull=True).first()
        consumers = self.producer.consumer_set.all()
        for consumer in consumers:
            if not consumer.last_reading or not consumer.last_reading >= production.time:
                # if not Reading.objects.filter(sensor=consumer.sensor, time__gte=production.time).exists():
                return False
        self.production = production
        self.consumers = consumers
        return True

    def _create_consumptions(self):
        """
        !!! Should only be called after _check_for_new_consumption !!!
        New Consumptions are created for Consumers of set producer
        """
        consumptions = {}
        for consumer in self.consumers:
            # next reading after the set production
            reading = Reading.objects.filter(sensor=consumer.sensor, time__gte=self.production.time).first()
            # last consumption of consumer
            last_consumption = consumer.consumption_set.last()
            target_time = self.production.time
            # right is the new reading
            right = {"time": reading.time, "value": reading.energy}
            left = {"time": last_consumption.time, "value": last_consumption.meter_reading}
            # interpolate meter_reading at target_time between left and right
            meter_reading = self._interpolate(left, right, target_time)
            consumptions[consumer.id] = {'meter_reading': meter_reading,
                                         # consumption is the difference of the meter readings
                                         'consumption': Decimal(meter_reading) - last_consumption.meter_reading,
                                         'last_consumption': last_consumption,
                                         'time': target_time,
                                         'consumer': consumer,
                                         'production': self.production}
        consumptions = self._divide_production_among_consumption(consumptions)
        for consumption in consumptions.values():
            del consumption['last_consumption']
            Consumption.objects.create(**consumption)

    def _interpolate(self, left, right, target_time):
        """
        interpolates a value at target_time linearly that is between base.value and base.time
        :param left: {value: number, time: datetime}
        :param right: {value: number, time: datetime}
        :param target_time: datetime
        :return: Decimal
        """
        difference = right['value'] - left['value']
        length = right['time'] - left['time']
        length_to_target = target_time - left['time']
        result = Decimal(left['value']) + (Decimal(difference) / Decimal(length.total_seconds())) * Decimal(
            length_to_target.total_seconds())
        print(f'got {float(left["value"])} at {left["time"]} \n'
              f'got {float(right["value"])} at {right["time"]} \n'
              f'calculated {result} at {target_time}')
        return result

    def _divide_production_among_consumption(self, consumptions):
        """
        !!!Must only run after in _create_consumptions!!! Divides the production of a producer to equally to the
        consumptions of all consumers that are related to the producer
        :param consumptions: {consumer__id: {meter_reading, consumption}}
        :return {consumer__id: {meter_reading, consumption, self_consumption, grid_consumption}}
        """
        # sort consumptions so that the consumer with the lowest consumption comes first
        consumptions = dict(sorted(consumptions.items(), key=lambda x: x[1]['meter_reading']))
        # production that is shared accross consumers -> in the beginning its all the production used
        available_production = self.production.used
        index = 0
        if available_production > 0:
            for consumption_key in consumptions:
                remaining_consumers = len(consumptions) - index
                consumption = consumptions[consumption_key]
                # each consumer gets an equal share
                share = available_production / remaining_consumers
                if consumption['consumption'] >= share:
                    consumption['self_consumption'] = share
                    consumption['grid_consumption'] = consumption['consumption'] - share
                else:  # if one consumer consumed less than the share -> every other consumer gets a bigger share
                    share = consumption['consumption']
                    consumption['self_consumption'] = consumption['consumption']
                    consumption['grid_consumption'] = 0
                    share -= consumption['consumption']
                available_production -= share
                self._assign_rate_and_price_to_consumption(consumption)
                index += 1
            if available_production > 0:
                print("Achtung: Produktion konnte nicht aufgeteilt werden")
        else:
            # if no production available than grid_consumption is all and self_consumption is 0
            for consumption_key in consumptions:
                consumptions[consumption_key]['grid_consumption'] = consumptions[consumption_key]['consumption']
                consumptions[consumption_key]['self_consumption'] = 0
                self._assign_rate_and_price_to_consumption(consumptions[consumption_key])
        pprint(consumptions)
        return consumptions

    def _assign_rate_and_price_to_consumption(self, consumption):
        """
        For given consumption, the
        :param consumption:  {meter_reading, time, last_consumption, self_consumption, ...}
        :return: consumption:  {...,  price, reduced_price, saved, grid_price, rate}
        """
        consumer = consumption['last_consumption'].consumer
        last_consumption_time = consumption['last_consumption'].time
        new_consumption_time = self.production.time
        # search for rate at new consumption time (= production time)
        # rates are filtered so the start_date and time match or are null
        rates = consumer.rates.all().filter(
            Q(start_date__lte=new_consumption_time.date()) | Q(start_date__isnull=True),
            Q(end_date__gte=new_consumption_time.date()) | Q(end_date__isnull=True),
            Q(start_time__lte=new_consumption_time.time()) | Q(start_time__isnull=True),
            Q(end_time__gte=new_consumption_time.time()) | Q(end_time__isnull=True)
        )
        # if multiple rates were found use the flexible
        if len(rates) > 1:
            rate = rates.get(flexible=True)
            if not rate:
                rate = rates.first()
        else:
            # else just use the first
            rate = rates.first()
        consumption['rate'] = rate
        # TODO: What if rate is not for the entire consumption span
        # price for used solar power
        consumption['reduced_price'] = Decimal(consumption['self_consumption'] * rate.reduced_price)
        # price for used grid power
        consumption['grid_price'] = Decimal(consumption['grid_consumption'] * rate.price)
        # sum_price
        consumption['price'] = consumption['reduced_price'] + consumption['grid_price']
        # saved money
        consumption['saved'] = (consumption['consumption'] * rate.price) - consumption['price']
        return consumption

    def _check_for_new_production(self):
        """
        Only returns true if there are production reading and grid reading that are younger than the last production
        time
        :return: Boolean
        """
        self.producer.refresh_from_db()
        print(type(self.producer.last_grid_reading), type(self.producer.last_production_reading))
        if not self.producer.last_production_reading \
                or not self.producer.last_production_reading > self.producer.production_set.last().time:
            return False
        if not self.producer.last_grid_reading \
                or not self.producer.last_grid_reading >= self.producer.last_production_reading:
            return False
        return True

    def _create_new_production(self):
        last_production = self.producer.production_set.last()
        new_production_reading = Reading.objects.filter(sensor__type="PM", time__gt=last_production.time,
                                                        sensor__producer=self.producer).first()
        new_grid_reading = Reading.objects.filter(sensor__type="GM", sensor__producer_grid=self.producer,
                                                  time__gte=new_production_reading.time).first()
        left = {'value': last_production.grid_meter_reading, 'time': last_production.time}
        right = {'value': new_grid_reading.energy, 'time': new_grid_reading.time}
        target_time = new_production_reading.time
        interpolated_grid_meter_reading = self._interpolate(left, right, target_time)
        new_production_data = {
            'producer': self.producer,
            'time': new_production_reading.time,
            'produced': Decimal(new_production_reading.energy) - last_production.production_meter_reading,
            'production_meter_reading': Decimal(new_production_reading.energy),
        }
        grid_feed_in = interpolated_grid_meter_reading - last_production.grid_meter_reading
        if grid_feed_in < 0:
            grid_feed_in = 0
            interpolated_grid_meter_reading = last_production.grid_meter_reading
        new_production_data['grid_feed_in'] = grid_feed_in
        if new_production_data['produced'] > grid_feed_in:
            # only the produced energy was really used that was not fed into the grid
            new_production_data['used'] = new_production_data['produced'] - grid_feed_in
            new_production_data['grid_meter_reading'] = interpolated_grid_meter_reading
        else:
            # because of the interpolation it is possible that a new production has fed more power in to the grid
            # than produced, which should be impossible. Therefore, in that case the grid_meter_reading is adjusted
            # so to the exact amount of actual production, so that "used" = 0. The rest of the grid_feed in will be
            #  considered in one of the next productions
            new_production_data['used'] = 0
            new_production_data['grid_meter_reading'] = left['value'] + new_production_data['produced']
            new_production_data['grid_feed_in'] = new_production_data['produced']
        new_production = Production.objects.create(**new_production_data)
        pprint(new_production_data)
