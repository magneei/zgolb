#!/usr/bin/env python3 

import yaml
import asyncio
import tibber
import aiohttp
import tsdb
from icecream import ic

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

def _callback(pkg):
    data = pkg.get("data")
    if data is None:
        return

    ic(data.get("liveMeasurement")['power'])
    tsdb.insert_ts("tibber","power",data.get("liveMeasurement")['power'])


from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

# Select your transport with a defined url endpoint
transport = WebsocketsTransport(url="wss://websocket-api.tibber.com/v1-beta/gql/subscriptions", headers={'Authorization': 'REDACTED'})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    f"""
    subscription{{
        liveMeasurement(homeId:"{config['tibber-home-id']}"){{
            timestamp
            power
            accumulatedConsumption
            accumulatedCost
            currency
            minPower
            averagePower
            maxPower
          }}
    }}
"""
)
# Execute the query on the transport
subgen = client.subscribe(query)

for result in subgen:
    ic(result['liveMeasurement']['power'],result['liveMeasurement']['timestamp'])
    tsdb.insert_ts("tibber","power",result['liveMeasurement']['power'])