import os
import pandas as pd

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

from devices.models import Device, location_category_information

load_dotenv()

url = os.getenv("INFLUX_DB_URL")
token = os.getenv("INFLUX_DB_TOKEN")
org = os.getenv("INFLUX_ORG")
bucket = os.getenv("INFLUX_BUCKET")
query = f'''
        from(bucket: "{bucket}")
        |> range(start: -3d)
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
            self.data = []
        else:
            data = []
            for table in query_result:
                for record in table.records:
                    data.append(
                        (record.get_time(), record.get_value(), record.values.get("deviceId")))
            self.data = data

    def prepare_data(self):
        df = pd.DataFrame(self.data)
        df.rename(columns={0: "datetime", 1: "db_level", 2: "device_id"}, inplace=True)
        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True, ascending=True)
        self.df = df

    def get_device_locations(self):
        devices = Device.objects.all()
        locations = {}
        for device in devices:
            if hasattr(device, 'location'):
                locations[device.device_id] = device.location
        self.locations = locations

    def aggregate_results(self):
        self.query_data()
        self.prepare_data()
        self.get_device_locations()
        grouped_data = self.df.groupby("device_id", sort=False)
        aggregated_data = []
        for name, group in grouped_data:
            if name not in self.locations:
                continue
            day = group.between_time("6:00", "22:00", inclusive="left")
            night = group.between_time("22:00", "6:00", inclusive="left")
            day_time_average = day_time_median = highest_day_noise = day_time_exceedances = 0
            night_time_average = night_time_median = highest_night_noise = night_time_exceedances = 0
            day_threshold = location_category_information[self.locations[name].category]["day_limit"]
            night_threshold = location_category_information[self.locations[name].category]["night_limit"]
            if not day.empty:
                day_time_average = day["db_level"].mean()
                day_time_median = day["db_level"].median()
                highest_day_noise = day["db_level"].max()
                day_time_exceedances = len(day[day["db_level"] > day_threshold])
            if not night.empty:
                night_time_average = night["db_level"].mean()
                night_time_median = night["db_level"].median()
                highest_night_noise = night["db_level"].max()
                night_time_exceedances = len(night[night["db_level"] > night_threshold])
            final = {
                "location": {
                    "city": self.locations[name].city,
                    "division": self.locations[name].division,
                    "parish": self.locations[name].parish,
                    "village": self.locations[name].village,
                    "noise_analysis": {
                        "day_time_average": day_time_average,
                        "day_time_median": day_time_median,
                        "day_time_exceedances": day_time_exceedances,
                        "highest_day_noise": highest_day_noise,
                        "night_time_average": night_time_average,
                        "night_time_median": night_time_median,
                        "night_time_exceedances": night_time_exceedances,
                        "highest_night_noise": highest_night_noise,
                        "night_time_quiet_hours": ""
                    }
                }
            }
            aggregated_data.append(final)
        return aggregated_data
