from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from base.serializers import UserSerializer, GroupSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class LogoutView(APIView):
    """
     In Basic TokenAuth a token does not expire. On logout the token gets destroyed, in order to force login
    """

    # TODO: error handeling
    def post(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        username = request.user.username
        return Response(f"{username} logged out successfully", status=status.HTTP_200_OK)


class CustomLogin(ObtainAuthToken):
    """
        Subcalls of built in token login view
        custom post function in order to return is_admin and the customer_id
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        is_admin = user.is_staff
        if is_admin:
            consumer_id = None
        else:
            consumer_id = user.consumer.id
        return Response({'token': token.key,
                         'is_admin': is_admin,
                         'consumer_id': consumer_id
                         })
