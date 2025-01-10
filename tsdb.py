import yaml
from icecream import ic
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

token = config['influx-token']
org = "charge"
url = "https://westeurope-1.azure.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def insert_ts(measurement, field, value):
    point = (
        Point(measurement)
        .field(field, value)
    )
    write_api.write(bucket="zgolb", org="charge", record=point)

def avg_measurement(measurement, field, minutes=5):
    query_api = client.query_api()

    query = f"""from(bucket: "zgolb")
    |> range(start: -{minutes}m)
    |> filter(fn: (r) => r._measurement == "{measurement}")
    |> filter(fn: (r) => r._field == "{field}")
    |> mean()"""
    tables = query_api.query(query, org="charge")

    avg = None

    for table in tables:
        for record in table.records:
            avg = record.get_value()

    return avg
