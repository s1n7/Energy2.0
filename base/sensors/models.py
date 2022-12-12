from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Sensor(models.Model):
    device_id = models.IntegerField()
    eui_id = models.IntegerField()


class Producer(models.Model):
    name = models.CharField(max_length=30)
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE)


class Consumer(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE)
