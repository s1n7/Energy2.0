import time

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from base.sensors.serializers import *
from base.sensors.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
class ConsumerView(viewsets.ModelViewSet):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProducerView(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SensorView(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# @api_view(['GET'])
# def populate_view(request):
#     if request.method == 'GET':
#         while True:
#             sensor = Sensor.objects.create(eui_id=123, device_id=123)
#             Producer.objects.create(name="Test", sensor=sensor)
#             print('created')
#             time.sleep(15)
#
#         return Response({"message": "Got some data!", "data": request.data})
#
#     # Messpunkt(Measuring) = (kWh, time)
#     # gegeben: Startzeit, Intervall n für 1/n, TimeArray
#     # TimeArray[24]: Für jede Stunde ein Sonnenfaktor(0=keine Sonne 1=normale Sonne 2=sehr Sonnig)
