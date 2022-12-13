import datetime

from django.db import models


# Create your models here.
from base.sensors.models import Sensor


class Reading(models.Model):
    power = models.DecimalField(max_digits=9, decimal_places=3)
    frequency = models.DecimalField(max_digits=5, decimal_places=3)
    voltage = models.DecimalField(max_digits=6, decimal_places=3)
    #TODO: jetzt mit default ist time theorethisch überschreibar, falls in den Daten ein Zeitstempel dabei ist.
    # ansonsten default löschen und auto_now_add=True damit time nicht mehr überschreibbar ist
    time = models.DateTimeField(default=datetime.datetime.now())
    sensor = models.ForeignKey(Sensor, on_delete=models.RESTRICT)
