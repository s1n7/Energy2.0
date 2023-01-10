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
        fields = ['url', 'username', 'email', 'groups', 'id', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @staticmethod
    def validate_password(value):
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


class AuthTokenSerializer(DRFAuthTokenSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                email = User.objects.filter(email=username)
                print(email)
                user = authenticate(request=self.context.get('request'),
                                    username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
