from abc import ABCMeta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer as DRFAuthTokenSerializer
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'id', 'password']
        extra_kwargs = {
            'password': {'write_only': True} # password is not displayed when user is serialized
        }

    @staticmethod
    def validate_password(value):
        validate_password(value)
        return value

    # TODO: can probably be deleted, was only for assigning groups to users
    def create(self, validated_data):
        # Groups können nicht direkt zugeordnet werden weil Many2Many Relationship
        if 'groups' in validated_data:
            user_groups = validated_data.pop('groups')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        # Many2Many Relationships brauchen ids deswegen vorher einmal abspeichern
        if 'groups' in validated_data:
            user.groups.set(user_groups)
            user.save()

        return user