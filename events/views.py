from rest_framework import viewsets

from .models import TrainEvent
from .serializers import TrainEventSerializer


class TrainEventViewSet(viewsets.ModelViewSet):
    queryset = TrainEvent.objects.all()
    serializer_class = TrainEventSerializer
# Create your views here.
