import time

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from energy2_backend import permissions as custom_permissions
from base.sensors.serializers import *
from base.sensors.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
class ConsumerView(viewsets.ModelViewSet):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [custom_permissions.UpdateAndReadOnlyOwned | permissions.IsAdminUser]


class ProducerView(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [permissions.IsAdminUser]


class SensorView(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.isAdminUser]
