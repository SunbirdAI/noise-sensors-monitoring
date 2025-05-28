# Pull base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# # Install cron
# RUN apt-get update
# RUN apt-get install -y cron

# Upgrade Pip
# RUN pip install --upgrade pip

# install a modern libpq and build deps for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq-dev     \
      gcc           \
 && rm -rf /var/lib/apt/lists/*


# Install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY . /code/
