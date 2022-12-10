#!/usr/bin/env python3 

import yaml
import asyncio
from python_graphql_client import GraphqlClient

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)


headers = {
	"Authorization": f"Bearer {config['tibber-token']}"
}

client = GraphqlClient(endpoint="https://api.tibber.com/v1-beta/gql",headers=headers)

query = """ 
{
  viewer {
    websocketSubscriptionUrl
  }
}
"""

data = client.execute(query=query)

sub_endpoint = data['data']['viewer']['websocketSubscriptionUrl']
sclient = GraphqlClient(endpoint=sub_endpoint,headers=headers)

query = """
subscription{
  liveMeasurement(homeId:"$homeId"){
    timestamp
    power
    accumulatedConsumption
    accumulatedCost
    currency
    minPower
    averagePower
    maxPower
  }
}
"""

variables = { "homeId": config['tibber-home-id']  }

data = asyncio.run(sclient.subscribe(query=query,variables=variables,handle=print))
