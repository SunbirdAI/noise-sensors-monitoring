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
        |> range(start: -1h)
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
        result = query_api.query(org=self._org, query=query)
        results = []
        for table in result:
            for record in table.records:
                results.append(
                    (record.get_time(), record.get_value(), record.values.get("deviceId")))
        self.results = results

    def aggregate_results(self):
        df = pd.DataFrame(self.results)
        df.rename(columns={0: "datetime", 1: "db_level", 2: "device_id"}, inplace=True)
        df.set_index("datetime", inplace=True)
        df = df.groupby("device_id", as_index=True).agg(["max", "mean", "median"])
        df.columns = df.columns.map("_".join)
        result = json.loads(df.to_json(orient="index"))
        print(result)
        return result


if __name__ == "__main__":
    client = InfluxClient()
    client.query_data()
    client.aggregate_results()
