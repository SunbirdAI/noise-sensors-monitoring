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
        query_result = []
        try:
            query_result = query_api.query(org=self._org, query=query)
        except Exception as exc:
            print(f"Error fetching data: {exc}")
        if not query_result:
            return None
        else:
            data = []
            for table in query_result:
                for record in table.records:
                    data.append(
                        (record.get_time(), record.get_value(), record.values.get("deviceId")))
            self.data = data

    def aggregate_results(self):
        df = pd.DataFrame(self.data)
        df.rename(columns={0: "datetime", 1: "db_level", 2: "device_id"}, inplace=True)
        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True, ascending=True)
        df_day = df.between_time("6:00", "22:00")
        df_night = df.between_time("22:00", "6:00")
        df_day.name = "day"
        df_night.name = "night"
        day = self.calculate_metrics(df_day)
        night = self.calculate_metrics(df_night)
        return [day, night]

    def calculate_metrics(self, df):
        grp = df.groupby("device_id", sort=False)
        results = []
        for name, group in grp:
            final = {
                "device_id": name,
                "noise_analysis": {
                    f"{df.name}_time_average": group["db_level"].mean(),
                    f"{df.name}_time_median": group["db_level"].median(),
                    f"highest_{df.name}_noise": group["db_level"].max(),
                    "night_time_quiet_hours": ""
                }
            }
            results.append(final)
        return results

if __name__ == "__main__":
    client = InfluxClient()
    client.query_data()
    client.aggregate_results()
