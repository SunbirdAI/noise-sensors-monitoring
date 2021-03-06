# Noise Sensor Monitoring
![Project Build](https://github.com/SunbirdAI/noise-sensors-monitoring/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/SunbirdAI/noise-sensors-monitoring/branch/main/graph/badge.svg?token=YOI8JHFD0S)](https://codecov.io/gh/SunbirdAI/noise-sensors-monitoring)

This repository contains code for the noise sensor monitoring project. At Sunbird AI we're using this application
to keep track of the sensors deployed in the field (i.e monitoring the battery level, signal strength). This application
also handles communication between the sensors and an external server (receiving audio files, configuring the sensors e.t.c).

## Technologies used
- [**Python**](https://www.python.org/) is the primary programming language used
- [**Grafana**](https://grafana.com/) used for visualization and creating the dashboard.
- [**InfluxDB**](https://www.influxdata.com/) is the time series database used to store key sensor metrics
- [**Eclipse Mosquitto**](https://mosquitto.org/) is the MQTT broker used to facilitate communication between the sensors
and the server.
- [**Docker**](https://www.docker.com/) and [**Docker-compose**](https://docs.docker.com/compose/) for spinning up containers
and using prebuilt containers.
- [**AWS**](https://aws.amazon.com/ec2) the system is deployed on an AWS EC2 instance.

### Key python packages used
- [Paho MQTT](https://pypi.org/project/paho-mqtt/) an MQTT Python client library.

## Set this project up locally
- Clone this repository and cd into this project's directory.
- (Optional) Add your mosquitto configuration in the file `./docker/mosquitto/config/mosquitto.conf`
- Make sure you have [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) installed
- Create an external docker network named `djangonetwork`. `docker network create -d bridge djangonetwork`. This allows easy communication between the different containers that will be running.
- Run the command `docker-compose up -d --build` to run the containers.
- To view logs (in case something fails to work): `docker-compose logs`
  (**TODO**: create docker build file for the mqtt_client step) 
- Visit `http:\\localhost:8086` to setup influx db.
    - You'll need to setup a username, an organization and a bucket. Refer to the influx db docs.
- Visit `http:\\localhost:3001` to view grafana and setup your dashboard.
    - Refer to the grafana docs for setting up an admin user
- Create `.env` file with the following info (Refer to the influxdb tutorial for how to get some of these):
```
INFLUX_DB_URL=http://localhost:8086
INFLUX_DB_TOKEN=<INSERT TOKEN HERE>
INFLUX_ORG=<YOUR-ORG>
INFLUX_BUCKET=<YOUR BUCKET>
MQTT_BROKER=localhost
```

## MQTT Topics Description
Below are the MQTT Topics implemented in this project.

|Topic    | Example Message                        | Description                                                                                                                   |
|---------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
|sb/sensor|{"deviceId": "SB1002", "dbLevel": 76...}| topic to which sensor sends its status. Required fields are `devicdId`, `dbLevel`, `connected`, `batteryLevel`, `sigStrength` |

**TODO**: Add description of the other topics as they're implemented.

## Setting up and running Django commands
- Ensure the containers are running. Use `docker ps` to see running containers.
- Apply the migrations using the command: `docker-compose exec web python manage.py migrate`
- Visit the app at `http://127.0.0.1:8000/`
- Use the following commands for running the tests:
  - Pytest tests (tests the functionality in the `noise_sensors_monitoring` package): `docker-compose exec web coverage run --source=noise_sensors_monitoring -m pytest`
  - Django tests: `docker-compose exec web coverage run -a --source=users manage.py test`
  - View coverage report `docker-compose exec web coverage report -m`

## API documentation
This project includes an API that serves our public `noise portal` front end app. <br/>
The documentation for the API endpoints is in this repository's wiki, [here](https://github.com/SunbirdAI/noise-sensors-monitoring/wiki/Noise-sensors-monitoring-API-docs).


## Deployment Steps
- Install Heroku CLI.
- Connect to the `noise-sensors-monitoring` app on heroku.
- Run the command `git push heroku main`.
- Apply the migrations: `heroku run python manage.py migrate`.
