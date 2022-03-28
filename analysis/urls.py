from django.urls import path
from .views import AnalysisView

urlpatterns = [
    path('', AnalysisView.as_view(), name='analysis'),
]
