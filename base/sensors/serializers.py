from base.contracts.models import Rate
from base.contracts.serializers import RateSerializer, ContractSerializer
from base.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from base.sensors.models import Consumer, Producer, Sensor
from django.db import transaction
from rest_framework.utils import model_meta


class NestedModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer that can manage multiple models being created/updated at once
    For example when creating Producer or Consumer a Sensor is created in the same process,
    """
    nested_serializers = None

    @transaction.atomic  # atomic, so if e.g. second object creation fails, first object creation is rolled back
    def create(self, validated_data):

        ModelClass = self.Meta.model
        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        nested_data = []
        for nested_serializer in self.nested_serializers:
            nested_name = nested_serializer[0]
            nested_class = nested_serializer[1]
            nested_data.append(validated_data.pop(nested_name))

        for i, nested_serializer in enumerate(self.nested_serializers):
            nested_name = nested_serializer[0]
            nested_class = nested_serializer[1]
            serializer = nested_class(data=nested_data[i])
            serializer.is_valid(raise_exception=True)
            new_entity = serializer.save()
            validated_data[nested_name] = new_entity

        instance = ModelClass.objects.create(**validated_data)

        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    """
        removes all nested data from request, because nested data is not supported by default method
    """

    def update(self, instance, validated_data):
        for model in self.nested_serializers:
            validated_data.pop(model[0], None)
        return super().update(instance, validated_data)


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sensor
        fields = "__all__"


class ConsumerSerializer(NestedModelSerializer):
    nested_serializers = [('sensor', SensorSerializer), ('user', UserSerializer)]

    id = serializers.IntegerField(read_only=True)
    sensor = SensorSerializer()
    user = UserSerializer()
    rates = serializers.HyperlinkedRelatedField(view_name="rate-detail", many=True,
                                                queryset=Rate.objects.all())

    class Meta:
        model = Consumer
        fields = "__all__"


class ProducerSerializer(NestedModelSerializer):
    nested_serializers = [('production_sensor', SensorSerializer), ('grid_sensor', SensorSerializer)]

    id = serializers.IntegerField(read_only=True)
    production_sensor = SensorSerializer()
    grid_sensor = SensorSerializer()

    class Meta:
        model = Producer
        fields = '__all__'
