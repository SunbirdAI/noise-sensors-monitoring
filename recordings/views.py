from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def receive_audio(request):
    audio_file = request.data['audio']

    return Response(f"Successfully received file {str(audio_file)}")
