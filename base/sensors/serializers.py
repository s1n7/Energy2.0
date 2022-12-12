from rest_framework import serializers
from base.sensors.models import Consumer, Producer, Sensor
from django.db import transaction


class MultiModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer that can manage multiple models being created/updated at once
    For example when creating Producer or Consumer a Sensor is created in the same process,
    """
    models = None

    @transaction.atomic
    def create(self, validated_data):
        ModelClass = self.Meta.model
        data = []
        for model in self.models:
            model_name = model[0]
            model_class = model[1]
            data.append(validated_data.pop(model_name))

        for i, model in enumerate(self.models):
            model_name = model[0]
            model_class = model[1]
            new_entity = model_class.objects.create(**data[i])
            validated_data[model_name] = new_entity

        return ModelClass.objects.create(**validated_data)


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sensor
        fields = "__all__"


class ConsumerSerializer(MultiModelSerializer):
    models = [('sensor', Sensor)]

    id = serializers.IntegerField(read_only=True)
    sensor = SensorSerializer()

    class Meta:
        model = Consumer
        fields = "__all__"


class ProducerSerializer(MultiModelSerializer):
    models = [('production_sensor', Sensor), ('grid_sensor', Sensor)]

    id = serializers.IntegerField(read_only=True)
    production_sensor = SensorSerializer()
    grid_sensor = SensorSerializer()

    class Meta:
        model = Producer
        fields = '__all__'
