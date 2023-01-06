import datetime

from base.contracts.models import Rate
from django.db import models

# Create your models here.
from base.sensors.models import Sensor, Consumer, Producer


class Reading(models.Model):
    power = models.DecimalField(max_digits=9, decimal_places=3)
    frequency = models.DecimalField(max_digits=5, decimal_places=3)
    voltage = models.DecimalField(max_digits=6, decimal_places=3)
    # TODO: jetzt mit default ist time theorethisch überschreibar, falls in den Daten ein Zeitstempel dabei ist.
    #  ansonsten default löschen und auto_now_add=True damit time nicht mehr überschreibbar ist
    time = models.DateTimeField(default=datetime.datetime.now)
    sensor = models.ForeignKey(Sensor, on_delete=models.RESTRICT)


class Production(models.Model):
    DECIMAL_PLACES = 10
    time = models.DateTimeField()
    produced = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    used = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    production_meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)
    grid_meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)

    producer = models.ForeignKey(Producer, on_delete=models.RESTRICT)


class Consumption(models.Model):
    DECIMAL_PLACES = Production.DECIMAL_PLACES
    time = models.DateTimeField()
    self_consumption = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    grid_consumption = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)
    price = models.DecimalField(max_digits=DECIMAL_PLACES + 4, decimal_places=DECIMAL_PLACES)

    rate = models.ForeignKey(Rate, on_delete=models.RESTRICT)
    production = models.ForeignKey(Production, on_delete=models.RESTRICT)
    consumer = models.ForeignKey(Consumer, on_delete=models.RESTRICT)
