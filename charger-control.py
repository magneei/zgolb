#!/usr/bin/env python3 

import tsdb
import time
import yaml
import zaptec
from math import sqrt
from icecream import ic

with open('config.yaml') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)

zpauth = zaptec.auth(config['zaptec-user'],config['zaptec-password'])

while(True):
    avg_power = tsdb.avg_measurement("tibber","power")
    ic(f"Average Power", avg_power)
    if(avg_power):
        zpdata = zaptec.charger_info(config['zaptec-charger-id'],zpauth)

        # Below is debug code for development, to be removed
        if('TotalChargePower' in zpdata):
            zpdata['TotalChargePower']
            print(zpdata['TotalChargePower'])
        else:
            print(zpdata)
        # end debug code 

        if(avg_power > config['power-threshold']):
            ic("Power over threshold")
            
            charging_budget = float(config['power-threshold']) - avg_power
            
            # amps calculated for IT real 3 phase charging 
            charging_budget_amps = int(charging_budget/230/sqrt(3))
            ic(f"Calculated {charging_budget_amps} before sanitizing")
            charging_budget_amps = min(32, charging_budget_amps)
            charging_budget_amps = max(6, charging_budget_amps)

            #check Zaptec (move dev code here)
            if('TotalChargePower' in zpdata):
                if(float(zpdata['TotalChargePower'] > charging_budget)):
                    ic(f"Threshold exceeded: Charging over budget, adjusting amps to {charging_budget_amps}")
                    zaptec.charge_amps(config['zaptec-charger-id'],zpauth,charging_budget_amps)
                else:
                    ic("Threshold exceeded: Not charging over budget, no adjustment")

    time.sleep(60)