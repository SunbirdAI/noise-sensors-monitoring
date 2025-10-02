/devices/locations/
/devices/config/
/device_metrics/environmental-parameters/ - devices environmental parameters records
/device_metrics/environmental-parameters/{id}/ - environmental parameter record id - (293118)
/device_metrics/devices/ - devices metrics records
/device_metrics/devices/{id}/ - device metrics record uuid - (d803a9ce-bf77-47f9-a495-fe70f381749a)
/device_metrics/sound-inference-data/ - sound inference data records
/device_metrics/sound-inference-data/{id}/ - sound inference data record id - (6816)


- for locations data use `/devices/locations/` endpoint then loop through to display on the frontend ui
- for MCU based sensors i.e (SB1004) from the device location data pick `device_name` and use the `/devices/devices/by-device-id/{device_id}/` endpoint to get more details about the device
- for AI based sensors i.e (SEAS-1, SEAS-2) from the device location data pick `device_name` and use the `/device_metrics/sound-inference-data/by-device-id/{device_id}/` endpoint to get latest sound inference data for the device and `/device_metrics/environmental-parameters/by-device-id/{device_id}/` endpoint to get latest environmental parameters data for the device