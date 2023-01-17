from rest_framework import serializers
from django.db import transaction

from base.data.models import Reading, Production, Consumption
from base.sensors.serializers import ConsumerSerializer


class ReadingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reading
        fields = '__all__'


class ProductionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Production
        fields = '__all__'


class ConsumptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Consumption
        fields = '__all__'
