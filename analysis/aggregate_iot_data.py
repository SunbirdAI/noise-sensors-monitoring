import pandas as pd
import pytz
from datetime import datetime

from noise_dashboard.settings import TIME_ZONE
from .models import DailyAggregate, HourlyAggregate
from devices.models import Device, location_category_information


class Aggregate:

    def __init__(self, data):
        self.data = data
        self.locations = self.get_device_locations()

    def get_device_locations(self):
        devices = Device.objects.all()
        locations = {}
        for device in devices:
            if hasattr(device, "location"):
                locations[device.device_id] = device.location
        return locations

    def prepare_data(self):
        df = pd.DataFrame(self.data)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def aggregate_hourly(self):
        df = self.prepare_data()
        df["hour"] = df["date"].dt.hour
        hour = df["hour"][0]
        threshold = None
        grouped_data = df.groupby("device_id", sort=False)
        for device_name, device_df in grouped_data:
            if hour >= 6 and hour < 22:
                threshold = location_category_information[self.locations[device_name].category]["day_limit"]
            else:
                threshold = location_category_information[self.locations[device_name].category]["night_limit"]

            HourlyAggregate.objects.create(
                device = Device.objects.get(device_id=device_name),
                date = device_df["date"][0],
                hour = hour,
                hourly_avg_db_level = device_df["db_level"].mean(),
                hourly_median_db_level = device_df["db_level"].median(),
                hourly_max_db_level = device_df["db_level"].max(),
                hourly_no_of_exceedances = len(device_df[device_df["db_level"] > threshold])
            )

        return None


    def aggregate_daily(self, time_period):
        df = self.prepare_data()
        threshold = None
        grouped_data = df.groupby("device_id", sort=False)
        for device_name, device_df in grouped_data:
            if time_period == "daytime":
                threshold = location_category_information[self.locations[device_name].category]["day_limit"]
            else:
                threshold = location_category_information[self.locations[device_name].category]["night_limit"]

            DailyAggregate.objects.create(
                device = Device.objects.get(device_id=device_name),
                date = device_df["date"][0],
                time_period = time_period,
                daily_avg_db_level = device_df["db_level"].mean(),
                daily_median_db_level = device_df["db_level"].median(),
                daily_max_db_level = device_df["db_level"].max(),
                daily_no_of_exceedances = len(device_df[device_df["db_level"] > threshold])
            )

        return None
