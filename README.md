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

## Run this project locally

The recommended local setup is Docker Compose. The Django app expects Postgres,
Redis, Mosquitto, InfluxDB, and Grafana to be available using the service names
defined in `docker-compose.yml`.

### 1. Prerequisites

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- Clone this repository and `cd` into the project directory.
- Make sure Docker Desktop is running before starting the services.

### 2. Create a local `.env`

The project loads `.env` automatically. For local development, use local values
and do not include production-only `RDS_*` variables, otherwise Django will try to
connect to the remote RDS database instead of the local `postgres_db` container.

Example local `.env`:

```env
ENVIRONMENT=development
DEBUG=False
SECRET_KEY=local-dev-secret-key
ALLOWED_HOSTS=localhost 127.0.0.1

MQTT_CLIENT_NAME=local_noise_monitor
MOSQUITTO_URL=Mosquitto
HTTP_APP_HOST=http://HTTPCLIENT:8000

INFLUX_DB_URL=http://localhost:8086
INFLUX_DB_TOKEN=<insert-local-influx-token>
INFLUX_ORG=<insert-local-influx-org>
INFLUX_BUCKET=<insert-local-influx-bucket>

# Optional: only needed when testing audio/metrics file uploads with S3 storage.
AWS_ACCESS_KEY_ID=<insert-aws-access-key>
AWS_SECRET_ACCESS_KEY=<insert-aws-secret-key>
AWS_STORAGE_BUCKET_NAME=<insert-bucket-name>
```

For a purely local database run, do not add `RDS_DB_NAME`, `RDS_HOSTNAME`,
`RDS_PASSWORD`, `RDS_PORT`, `RDS_USERNAME`, or `DATABASE_URL` to `.env`.

### 3. Start the Docker services

Create the shared Docker network once:

```bash
docker network create -d bridge djangonetwork
```

If it already exists, Docker will tell you. That is fine.

Build and start the stack:

```bash
docker compose up -d --build
```

Apply database migrations:

```bash
docker compose exec web python manage.py migrate
```

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Open the local services

- Internal dashboard: `http://127.0.0.1:8000/`
- Devices dashboard: `http://127.0.0.1:8000/devices/`
- Django admin: `http://127.0.0.1:8000/admin/`
- API docs: `http://127.0.0.1:8000/api/docs/`
- InfluxDB: `http://127.0.0.1:8086/`
- Grafana: `http://127.0.0.1:3001/`
- Mosquitto MQTT broker: `localhost:1883`

### 5. Useful local commands

View running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f web
```

Run tests:

```bash
docker compose exec web python manage.py test
docker compose exec web coverage run --source=noise_sensors_monitoring,mqtt -m pytest
docker compose exec web coverage report -m
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove local Docker volumes:

```bash
docker compose down -v
```

Use `docker compose down -v` only when you are comfortable deleting local
Postgres, InfluxDB, and Grafana data.

### Local troubleshooting

- If Django cannot connect to Postgres, confirm that `.env` does not contain
  `RDS_*` or `DATABASE_URL` values.
- If the MQTT container exits immediately, confirm `MQTT_CLIENT_NAME` is set in
  `.env`.
- If file uploads fail locally, configure AWS/S3 values or adjust storage for
  local development.
- If Docker reports that `djangonetwork` already exists, continue with
  `docker compose up -d --build`.

## MQTT Topics Description
Below are the MQTT Topics implemented in this project.

|Topic    | Example Message                        | Description                                                                                                                   |
|---------|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
|sb/sensor|{"deviceId": "SB1002", "dbLevel": 76...}| topic to which sensor sends its status. Required fields are `devicdId`, `dbLevel`, `connected`, `batteryLevel`, `sigStrength` |

**TODO**: Add description of the other topics as they're implemented.

## Running Django commands

Run Django commands inside the `web` container:

```bash
docker compose exec web python manage.py <command>
```

Common examples:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose exec web python manage.py shell
```

## API documentation
This project includes an API that serves our public `noise portal` front end app. <br/>
The documentation for the API endpoints is in this repository's wiki, [here](https://github.com/SunbirdAI/noise-sensors-monitoring/wiki/Noise-sensors-monitoring-API-docs).


## Deployment Steps
- Install Heroku CLI.
- Connect to the `noise-sensors-monitoring` app on heroku.
- Run the command `git push heroku main`.
- Apply the migrations: `heroku run python manage.py migrate`.
