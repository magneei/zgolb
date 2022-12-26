from tinyflux import TinyFlux
from tinyflux import Point
from datetime import datetime,timezone, timedelta
from tinyflux import TimeQuery
from icecream import ic

db = TinyFlux("zgolb.db")

def insert_ts(measurement, field, value):
    p = Point(
        measurement=measurement,
        time=datetime.now(timezone.utc),
        tags={},
        fields={field: value}
    )

    db.insert(p)

def avg_measurement(measurement, field, minutes=5):
    Time = TimeQuery()

    q1 = Time > datetime.now(timezone.utc)-timedelta(minutes=minutes)
    q2 = Time < datetime.now(timezone.utc)

    data = db.search(q1 & q2)

    if data:
        avg = sum([ p.fields[field] for p in data ]) / len(data)
    else: 
        ic('No data available')
        avg = None 
    
    return avg
