from rest_framework import viewsets, parsers

from .models import Recording
from .serializers import UploadRecordingSerializer


class ReceiveAudioViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = UploadRecordingSerializer
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['post']

    # def finalize_response(self, request, response, *args, **kwargs):
    #     if response.status_code != 201:
    #         print(response.data)
    #         response.data = {"Failed"}
    #     return super(ReceiveAudioViewSet, self).finalize_response(request, response, *args, **kwargs)
