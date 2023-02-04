from rest_framework import viewsets
from rest_framework import permissions
from base.contracts.models import *
from base.contracts.serializers import ContractSerializer, RateSerializer


# Create your views here.


class ContractView(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAdminUser]


class RateView(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [permissions.IsAdminUser]
