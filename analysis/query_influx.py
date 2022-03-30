import os
import json
import pandas as pd

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

from django.http import JsonResponse

load_dotenv()

url = os.environ["INFLUX_DB_URL"]
token = os.environ["INFLUX_DB_TOKEN"]
org = os.environ["INFLUX_ORG"]
bucket = os.environ["INFLUX_BUCKET"]
query = f'''
        from(bucket: "{bucket}")
        |> range(start: -24h)
        |> filter(fn: (r) => r["_measurement"] == "DB_LEVEL")
        |> filter(fn: (r) => r["_field"] == "db_level")
'''


class InfluxClient:
    def __init__(self, token=token, org=org, bucket=bucket, url=url):
        self._org = org
        self._bucket = bucket
        self.url = url
        self._client = InfluxDBClient(url=url, token=token)

    def query_data(self, query=query):
        query_api = self._client.query_api()
        query_result = query_api.query(org=self._org, query=query)
        data = []
        for table in query_result:
            for record in table.records:
                data.append(
                    (record.get_time(), record.get_value(), record.values.get("deviceId")))
        self.data = data

    def aggregate_results(self):
        df = pd.DataFrame(self.data)
        df.rename(columns={0: "datetime", 1: "db_level", 2: "device_id"}, inplace=True)
        grp = df.groupby("device_id", sort=False)
        results = []
        for name, group in grp:
            final = {
                "device_id": name,
                "noise_analysis": {
                    "average": group["db_level"].mean(),
                    "median": group["db_level"].median(),
                    "max": group["db_level"].max()
                }
            }
            results.append(final)
        return results


if __name__ == "__main__":
    client = InfluxClient()
    client.query_data()
    client.aggregate_results()
