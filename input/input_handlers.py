import datetime
from decimal import Decimal
from pprint import pprint

from base.data.models import Reading, Production
from base.sensors.models import Sensor
from django.db.models import Q


class InputHandler:

    def __init__(self, request, producer):
        self.producer = producer
        self.request = request
        self.sensor = None
        self.data = None

    def handle_input(self):
        # if request is none, no reading should be created but check for new possible productions or consumptions
        st = datetime.datetime.now()
        if self.request is not None:
            request = self.request
            device_id = self.request.data.device_id
            self.data = request.data.parsed
            # from request get device_id and get the according sensor instance
            # TODO: What if no sensor with id exists
            self.sensor = Sensor.objects.find(device_id=device_id)
            sensor = self.sensor
            # Depending on the sensor type the according producer has to be fetched differently
            if sensor.type == "CM":  # Consumption Meter
                self.producer = sensor.consumer.producer
            elif sensor.type == "PM":  # Production Meter
                self.producer = sensor.producer
            elif sensor.type == "GM":  # Grid Meter
                self.producer = sensor.producer_grid
            self._save_input_as_reading()
        if self._check_for_new_consumption():
            self._create_consumptions()
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
            'time': data['source_time'],
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
            # TODO: add last_reading field to consumer model to make check faster
            if not consumer.last_reading >= production.time: # this is the fullfilles TODO hopefully
            # if not Reading.objects.filter(sensor=consumer.sensor, time__gte=production.time).exists():
                return False
        self.production = production
        self.consumers = consumers
        return True

    def _create_consumptions(self):
        """
        !!! Should only be called after _check_for_new_consumption
        New Consumptions are created for Consumers of set producer
        """
        consumptions = {}
        for consumer in self.consumers:
            # closest reading that is younger than set production
            reading = Reading.objects.filter(sensor=consumer.sensor, time__gte=self.production.time).first()
            # last consumption of consumer
            last_consumption = consumer.consumption_set.last()
            target_time = self.production.time
            subject = {"time": reading.time, "value": reading.energy}
            base = {"time": last_consumption.time, "value": last_consumption.meter_reading}
            # interpolate meter_reading at target_time
            meter_reading = self._interpolate(base, subject, target_time)
            consumptions[consumer.id] = {'meter_reading': meter_reading,
                                         'consumption': Decimal(meter_reading) - last_consumption.meter_reading,
                                         'last_consumption': last_consumption}
        consumptions = self._divide_production_among_consumption(consumptions)

    def _interpolate(self, base, subject, target_time):
        """
        interpolates a value at target_time linearly that is between base.value and base.time
        :param base: {value: number, time: datetime}
        :param subject: {value: number, time: datetime}
        :param target_time: datetime
        :return: Decimal
        """
        difference = subject['value'] - base['value']
        length = subject['time'] - base['time']
        length_to_target = target_time - base['time']
        result = Decimal(base['value']) + (Decimal(difference) / Decimal(length.total_seconds())) * Decimal(
            length_to_target.total_seconds())
        return result

    def _divide_production_among_consumption(self, consumptions):
        """
        !!!Must only run after in _create_consumptions!!!
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
                share = available_production / remaining_consumers
                if consumption['consumption'] >= share:
                    consumption['self_consumption'] = share
                    consumption['grid_consumption'] = consumption['consumption'] - share
                else:
                    share = consumption['consumption']
                    consumption['self_consumption'] = share
                    consumption['grid_consumption'] = 0
                self._assign_rate_and_price_to_consumption(consumption)
                available_production -= share
                index += 1
        else:
            # if no production avalibale than grid_consumption is all and self_consumption is 0
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
            #else just use the first
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
        # TODO: change to last_reading on Producer
        grid_sensor = self.producer.grid_sensor
        last_production = self.producer.production_set.last()
        producer_reading = self.producer.production_sensor.reading_set.filter(time__gt=last_production.time).first()
        if not producer_reading:
            return False
        grid_reading = grid_sensor.reading_set.filter(sensor=grid_sensor, time__gte=producer_reading.time).first()
        if not grid_reading:
            return False