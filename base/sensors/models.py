from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Sensor(models.Model):

    class SensorTypes(models.TextChoices):
        PRODUCTION_METER = 'PM', 'Production Meter'
        CONSUMPTION_METER = 'CM', 'Consumption Meter'
        GRID_METER = 'GM', 'Grid Meter'
    # ID an der wir am Ende Sensor einer WE zuordnen können, wahrscheinlich ZählerNr oder so
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
    production_sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT)
    grid_sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT, related_name="grid_sensor")


class Consumer(models.Model):
    name = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    sensor = models.OneToOneField(Sensor, on_delete=models.RESTRICT)
