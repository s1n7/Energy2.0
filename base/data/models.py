import datetime

from base.contracts.models import Rate
from django.db import models

# Create your models here.
from base.sensors.models import Sensor, Consumer, Producer
from django.db.models.signals import post_save
from django.dispatch import receiver


class Reading(models.Model):
    energy = models.DecimalField(max_digits=10, decimal_places=4)
    power = models.DecimalField(max_digits=9, decimal_places=4)
    # TODO: jetzt mit default ist time theorethisch überschreibar, falls in den Daten ein Zeitstempel dabei ist.
    #  ansonsten default löschen und auto_now_add=True damit time nicht mehr überschreibbar ist
    time = models.DateTimeField(default=datetime.datetime.now)
    sensor = models.ForeignKey(Sensor, on_delete=models.RESTRICT)


@receiver(post_save, sender=Reading)
def update_last_reading(instance, sender, *args, **kwargs):
    sensor = instance.sensor
    if sensor.type == "CM":
        entity = sensor.consumer
        entity.last_reading = instance.time
    elif sensor.type == "PM":
        entity = sensor.producer
        entity.last_production_reading = instance.time
    elif sensor.type == "GM":
        entity = sensor.producer_grid
        entity.last_grid_reading = instance.time
    entity.save()


class Production(models.Model):
    DECIMAL_PLACES = 10
    time = models.DateTimeField()
    produced = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    used = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    production_meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)
    grid_meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)
    grid_feed_in = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    producer = models.ForeignKey(Producer, on_delete=models.RESTRICT)


class Consumption(models.Model):
    DECIMAL_PLACES = Production.DECIMAL_PLACES
    time = models.DateTimeField()
    self_consumption = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    grid_consumption = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    consumption = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)
    meter_reading = models.DecimalField(max_digits=DECIMAL_PLACES + 5, decimal_places=DECIMAL_PLACES)
    price = models.DecimalField(max_digits=DECIMAL_PLACES + 4, decimal_places=DECIMAL_PLACES)
    reduced_price = models.DecimalField(max_digits=DECIMAL_PLACES + 4, decimal_places=DECIMAL_PLACES)
    grid_price = models.DecimalField(max_digits=DECIMAL_PLACES + 4, decimal_places=DECIMAL_PLACES)
    saved = models.DecimalField(max_digits=DECIMAL_PLACES + 3, decimal_places=DECIMAL_PLACES)

    rate = models.ForeignKey(Rate, on_delete=models.RESTRICT)
    production = models.ForeignKey(Production, on_delete=models.RESTRICT)
    consumer = models.ForeignKey(Consumer, on_delete=models.RESTRICT)
