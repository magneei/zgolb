#!/usr/bin/env python3 

import yaml
from python_graphql_client import GraphqlClient

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

print(config)
client = GraphqlClient(endpoint="https://api.tibber.com")
print(dir(client))
client.inject_token(config['tibber-token'])
