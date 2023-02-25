from datetime import datetime as dt

from django.core.exceptions import BadRequest
from rest_framework import viewsets
from rest_framework import permissions

# Create your views here.
from base.data.models import *
from base.data.serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class ReadingView(viewsets.ModelViewSet):
    serializer_class = ReadingSerializer
    queryset = Reading.objects.all()


class ProductionView(viewsets.ModelViewSet):
    serializer_class = ProductionSerializer
    queryset = Production.objects.all()


class ConsumptionView(viewsets.ModelViewSet):
    serializer_class = ConsumptionSerializer
    queryset = Consumption.objects.all()


@api_view(['POST', ])
@permission_classes([permissions.IsAdminUser])
def setup_data_view(request):
    if request.method == "POST":
        id = request.data.get('producer_id')
        try:
            timestamp = dt.strptime(request.data.get('timestamp'), "%Y-%m-%dT%H:%M:%S")
        except:
            raise BadRequest("Falsches Datumsformat, benutze: %Y-%m-%dT%H:%M:%S")
        print(id, timestamp)
        if id and timestamp:
            try:
                producer = Producer.objects.get(id=id)
                if len(producer.production_set.all()) == 0:
                    production = Production.objects.create(producer=producer, grid_meter_reading=0,
                                                           production_meter_reading=0, time=timestamp, produced=0,
                                                           used=0, grid_feed_in=0)
                    for c in producer.consumer_set.all():
                        Consumption.objects.create(self_consumption=0, grid_consumption=0, meter_reading=0,
                                                   consumer=c, time=timestamp, production=production, price=0,
                                                   rate=Rate.objects.first(), grid_price=0, reduced_price=0,
                                                   saved=0, consumption=0)
                else:
                    return Response("Daten bereits vorhanden, kein Setup möglich/notwendig", 208)
            except Exception as e:
                raise NotFound()
        else:
            raise BadRequest()

    return Response(200)
