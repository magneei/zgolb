#!/usr/bin/env python3 

import yaml
import asyncio
import tibber
import aiohttp
import tsdb

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

def _callback(pkg):
    data = pkg.get("data")
    if data is None:
        return

    #print(data.get("liveMeasurement"))
    print(data.get("liveMeasurement")['power'])
    tsdb.insert_ts("tibber","power",data.get("liveMeasurement")['power'])

async def run():
    await asyncio.sleep(1)

    async with aiohttp.ClientSession() as session: 
        tibber_connection = tibber.Tibber(config['tibber-token'], websession=session, user_agent="zgolb")
        await tibber_connection.update_info()

    await asyncio.sleep(1)

    home = tibber_connection.get_homes()[0]
    await home.rt_subscribe(_callback)

    while(True):
      await asyncio.sleep(1000)

async def test(): 
  tibber_connection = tibber.Tibber(config['tibber-token'], user_agent="zgolb")
  await tibber_connection.update_info()
  print(tibber_connection.name)

  home = tibber_connection.get_homes()[0]
  await home.update_info()
  print(home.address1)

  await home.update_price_info()
  print(home.current_price_info)

  await tibber_connection.close_connection()

asyncio.run(run())