from rest_framework import viewsets, parsers
from rest_framework.response import Response

from .models import Recording
from .serializers import UploadRecordingSerializer
from devices.serializers import RecordingSerializer


class UpdateAudioViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    http_method_names = ['patch']
    lookup_field = 'id'

    def partial_update(self, request, *args, **kwargs):
        instance = self.queryset.get(id=kwargs.get('id'))
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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
