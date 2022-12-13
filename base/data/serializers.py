from rest_framework import serializers
from django.db import transaction

from base.data.models import Reading
from base.sensors.serializers import ConsumerSerializer


class ReadingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Reading
        fields = '__all__'