from django.contrib import admin
from base.sensors.models import Producer, Consumer

# Register your models here.

admin.site.register(Producer)
admin.site.register(Consumer)