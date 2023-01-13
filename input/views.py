import datetime
from pprint import pprint

from base.contracts.models import Rate
from base.data.models import Reading, Production, Consumption
from base.sensors.models import Sensor
from django.db.models import Q
from input.input_handlers import InputHandler
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from decimal import Decimal
from rest_framework.response import Response


# Create your views here.

@api_view(['POST', ])
@permission_classes([permissions.AllowAny])
def input_view(request):
    input_handler = InputHandler(request)
    input_handler.handle_input()

    return Response(status=200)
