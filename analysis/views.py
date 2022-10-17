from rest_framework.response import Response
from rest_framework.views import APIView

from .aggregate_influx_data import InfluxClient

class AnalysisView(APIView):

    def get(self, request):
        client = InfluxClient()
        results = client.aggregate_results()
        return Response(results)
