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
    """
    Add Query Param producer_id=:id: to the request, in order to filter only for Consumers of given Producer
    """
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer
    permission_classes = [custom_permissions.UpdateAndReadOnlyOwned | permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Consumer.objects.all()
        producer_id = self.request.query_params.get('producer_id')
        if producer_id is not None:
            queryset = queryset.filter(producer_id=producer_id)
        return queryset



class ProducerView(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    permission_classes = [permissions.IsAdminUser]


class SensorView(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAdminUser]
