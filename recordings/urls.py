from django.urls import path
from .views import receive_audio


urlpatterns = [
    path('', receive_audio),
]
