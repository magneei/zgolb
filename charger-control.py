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
    avg_charge = tsdb.avg_measurement("zaptec","chargepower")

    if(avg_charge is None):
        avg_charge = 0

    ic("Average", avg_power, avg_charge)
    if(avg_power):
        zpdata = zaptec.charger_info(config['zaptec-charger-id'],zpauth)

        if(avg_power > config['power-threshold']):
            ic("Power over threshold")
            
        charging_budget = float(config['power-threshold']) - avg_power + avg_charge
        
        # amps calculated for IT real 3 phase charging 
        charging_budget_amps = int(charging_budget/230/sqrt(3))
        ic("Calculated amps before sanitizing",charging_budget_amps)
        charging_budget_amps = min(32, charging_budget_amps)
        charging_budget_amps = max(6, charging_budget_amps)

        #check Zaptec (move dev code here)
        if('TotalChargePower' in zpdata):
            tsdb.insert_ts("zaptec","chargepower",float(zpdata['TotalChargePower']))

            #Remove if True for adjustment only when actually charging (to reduce api calls)
            if(float(zpdata['TotalChargePower']) > 0 or True):
                ic("Adjusting amps to budget", charging_budget_amps)
                zaptec.charger_set_amps(config['zaptec-installation-id'],zpauth,charging_budget_amps)

    time.sleep(60)
