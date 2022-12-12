from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups', 'id', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # Groups können nicht direkt zugeordnet werden weil Many2Many Relationship
        user_groups = validated_data.pop('groups')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        # Many2Many Relationships brauchen ids deswegen vorher einmal abspeichern
        user.groups.set(user_groups)
        user.save()

        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name', 'id']
