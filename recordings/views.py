from rest_framework import viewsets, parsers

from .models import Recording
from .serializers import RecordingSerializer


class ReceiveAudioViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['post']
