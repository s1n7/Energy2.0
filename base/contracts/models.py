import datetime

from django.db import models


# Create your models here.

class Rate(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=6, decimal_places=3)
    reduced_price = models.DecimalField(max_digits=6, decimal_places=3)

    flexible = models.BooleanField(default=False)

    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


class Contract(models.Model):
    name = models.CharField(max_length=30)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    rates = models.ManyToManyField(Rate)
