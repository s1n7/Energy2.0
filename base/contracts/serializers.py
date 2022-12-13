from rest_framework import serializers
from base.contracts.models import Contract, Rate


class ContractSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Contract
        fields = '__all__'


class RateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Rate
        fields = '__all__'

