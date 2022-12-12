from rest_framework import serializers
from base.sensors.models import Consumer, Producer, Sensor
from django.db import transaction


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sensor
        fields = "__all__"


class ConsumerSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    sensor = SensorSerializer()

    class Meta:
        model = Consumer
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        # remove all data related to new sensor
        sensor = validated_data.pop('sensor')
        sensor = Sensor.objects.create(**sensor)
        # set created sensor on new consumer
        validated_data['sensor'] = sensor
        consumer = Consumer.objects.create(**validated_data);

        return consumer


class ProducerSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    sensor = SensorSerializer()

    class Meta:
        model = Producer
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        # remove all data related to new sensor
        sensor = validated_data.pop('sensor')
        sensor = Sensor.objects.create(**sensor)
        # set created sensor on new consumer
        validated_data['sensor'] = sensor
        producer = Producer.objects.create(**validated_data);

        return producer
