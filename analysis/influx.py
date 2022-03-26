import os

# import pandas as pd
from dotenv import load_dotenv

from django.http import JsonResponse
from influxdb_client import InfluxDBClient

load_dotenv()

url=os.environ["INFLUX_DB_URL"]
token=os.environ["INFLUX_DB_TOKEN"]
org=os.environ["INFLUX_ORG"]
bucket = os.environ["INFLUX_BUCKET"]

client = InfluxDBClient(url=url, token=token, org=org)

def get_data():
    query_api = client.query_api()
    query = f'''
        from(bucket: "{bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "DB_LEVEL")
        |> filter(fn: (r) => r["_field"] == "db_level")
    '''
    result = query_api.query(query)
    return JsonResponse(result)

    # results = []
    # for table in result:
    #     for record in table.records:
    #         results.append((record.get_time(), record.get_field(), record.get_value(), record.values.get("deviceId")))
    
    # print(len(results))
    # df = pd.DataFrame(results)
    # print(df.head())

if __name__=='__main__':
    get_data()
