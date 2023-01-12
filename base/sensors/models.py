from django.db import models
from django.contrib.auth.models import User


# Create your models here.
from base.contracts.models import Contract, Rate


class Sensor(models.Model):

    class SensorTypes(models.TextChoices):
        PRODUCTION_METER = 'PM', 'Production Meter'
        CONSUMPTION_METER = 'CM', 'Consumption Meter'
        GRID_METER = 'GM', 'Grid Meter'
    # ID an der wir am Ende Sensor einer WE zuordnen können, wahrscheinlich ZählerNr/EUI oder so
    device_id = models.IntegerField()
    type = models.CharField(
        max_length=2,
        choices=SensorTypes.choices
    )


class Producer(models.Model):
    name = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=5)
    city = models.CharField(max_length=20)
    peak_power = models.IntegerField()
    production_sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT, related_name="producer")
    # set related name to distinguish between sensor.producer and sensor.producer_grid
    # (access to producer if sensor is set as production sensor and if sensor is set as grid_sensor)
    grid_sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT, related_name="producer_grid")
    last_production_reading = models.DateTimeField(null=True)
    last_grid_reading = models.DateTimeField(null=True)


class Consumer(models.Model):
    name = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    producer = models.ForeignKey(Producer, on_delete=models.RESTRICT)
    sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT)
    #contract = models.ForeignKey(Contract, on_delete=models.RESTRICT)
    rates = models.ManyToManyField(Rate, through=Contract)
    last_reading = models.DateTimeField(null=True)
