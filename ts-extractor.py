#!/usr/bin/env python3

import yaml
import asyncio
import aiohttp
import tsdb
from icecream import ic
from time import sleep
from websockets.exceptions import ConnectionClosedError
import watchdog
import sys

# Constants
WATCHDOG_TIMER = 180

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

# Select your transport with a defined url endpoint
transport = WebsocketsTransport(
    url="wss://websocket-api.tibber.com/v1-beta/gql/subscriptions",
    headers={"Authorization": "b-alwMawfx4RGN1Mch-LyBElLUXDvx_HXrxxNumqmlk"},
)


def wdHandler():
    ic("No data received for time limit, quitting", WATCHDOG_TIMER)
    runstatus = False
    sys.exit(1)

wd = watchdog.Watchdog(WATCHDOG_TIMER, wdHandler)

client = None
runstatus = True


def main():
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
        ic(
            result["liveMeasurement"]["power"],
            result["liveMeasurement"]["timestamp"],
        )
        tsdb.insert_ts("tibber", "power", result["liveMeasurement"]["power"])
        wd.reset()


while True:
    try:
        main()
    except ConnectionClosedError:
        ic("Received connectionClosedError, quitting")
        sys.exit(1)
        ic("exit failed")
    sleep(10)
