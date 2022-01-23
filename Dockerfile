FROM python:3.10.1-bullseye

# Environmental Variables
ENV INFLUXDB_HOST = 
ENV INFLUXDB_PORT = 8086
ENV INFLUXDB_USERNAME = 
ENV INFLUXDB_PASSWORD = 
ENV INFLUXDB_DATABASE = 
ENV INFLUXDB_MEASUREMENT = bulb/energyreadings
ENV BULB_ACCOUNT = 
ENV BULB_TOKEN = 
ENV REFRESH_TIME = 900

# Set up virtual environment
RUN python3 -m venv /opt/venv

# Install dependencies:
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install -r requirements.txt

# Run the application:
COPY main.py .
COPY bulb.py .
COPY db.py .
CMD . /opt/venv/bin/activate && exec python -u main.py
