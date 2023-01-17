from rest_framework import viewsets
from rest_framework import permissions

# Create your views here.
from base.data.models import *
from base.data.serializers import *


class ReadingView(viewsets.ModelViewSet):
    serializer_class = ReadingSerializer
    queryset = Reading.objects.all()


class ProductionView(viewsets.ModelViewSet):
    serializer_class = ProductionSerializer
    queryset = Production.objects.all()


class ConsumptionView(viewsets.ModelViewSet):
    serializer_class = ConsumptionSerializer
    queryset = Consumption.objects.all()
