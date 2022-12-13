from rest_framework import viewsets
from rest_framework import permissions

# Create your views here.
from base.data.models import Reading
from base.data.serializers import ReadingSerializer


class ReadingView(viewsets.ModelViewSet):
    serializer_class = ReadingSerializer
    queryset = Reading.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]