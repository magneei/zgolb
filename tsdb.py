import yaml
from tinyflux import TinyFlux
from tinyflux import Point
from datetime import datetime,timezone, timedelta
from tinyflux import TimeQuery
from tinyflux import MeasurementQuery
from icecream import ic
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

db = TinyFlux("zgolb.db")

token = config['influx-token']
org = "charge"
url = "https://westeurope-1.azure.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

def insert_ts(measurement, field, value):
    point = (
        Point(measurement)
        .field(field, value)
    )
    client.write_api.write(bucket="zgolb", org="charge", record=point)

def avg_measurement(measurement, field, minutes=5):
    Time = TimeQuery()

    q1 = Time > datetime.now(timezone.utc)-timedelta(minutes=minutes)
    q2 = Time < datetime.now(timezone.utc)

    m = db.measurement(measurement)
    data = m.search(q1 & q2)

    if data:
        #avg = sum([p.fields[field] for p in data ]) / len(data)
        sum = 0
        for p in data:
            ic(p)
            sum += p.fields[field]
        avg = sum/len(data)
    else: 
        ic('No data available')
        avg = None 
    
    return avg
