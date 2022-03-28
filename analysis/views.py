from django.http import JsonResponse

from query_influx import InfluxClient

def analysis(request):
    client = InfluxClient()
    client.query_data()
    results = client.aggregate_results()
    return JsonResponse(results)
