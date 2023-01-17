from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from base.serializers import UserSerializer, GroupSerializer
from rest_framework import status
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
    #TODO: error handeling
    def post(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        username = request.user.username
        return Response(f"{username} logged out successfully", status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
