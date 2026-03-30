#!/usr/bin/env python3

import tsdb
import time
import yaml
import zaptec
from math import sqrt
from icecream import ic

POWER_MIN_AMPS = 6
POWER_MAX_AMPS = 32

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

zpauth = zaptec.auth(config["zaptec-user"], config["zaptec-password"])

while True:
    avg_power = tsdb.avg_measurement("tibber", "power")
    avg_charge = tsdb.avg_measurement("zaptec", "chargepower")

    if avg_charge is None:
        avg_charge = 0

    ic("Average", avg_power, avg_charge)

    zpdata = zaptec.charger_info(config["zaptec-charger-id"], zpauth)
    
    # Log all relevant charging data
    for field in [
        "TotalChargePower",
        "CurrentPhase1",
        "CurrentPhase2",
        "CurrentPhase3",
        "VoltagePhase1",
        "VoltagePhase2",
        "VoltagePhase3",
        "ActivePhases"
    ]:
        if field in zpdata:
            measurement_name = field.lower().replace("phase", "_l")
            tsdb.insert_ts("zaptec", measurement_name, float(zpdata[field]))


    # Get per-phase current readings
    current_l1 = tsdb.avg_measurement("tibber", "currentL1")
    current_l2 = tsdb.avg_measurement("tibber", "currentL2")
    current_l3 = tsdb.avg_measurement("tibber", "currentL3")
    
    # Get charger phase currents
    charge_l1 = tsdb.avg_measurement("zaptec", "current_l1")
    charge_l2 = tsdb.avg_measurement("zaptec", "current_l2")
    charge_l3 = tsdb.avg_measurement("zaptec", "current_l3")

    # Set to 0 if no charging data
    charge_l1 = charge_l1 if charge_l1 is not None else 0
    charge_l2 = charge_l2 if charge_l2 is not None else 0
    charge_l3 = charge_l3 if charge_l3 is not None else 0

    ic("House currents", current_l1, current_l2, current_l3)
    ic("Charge currents", charge_l1, charge_l2, charge_l3)

    if all([current_l1, current_l2, current_l3]):  # Make sure we have all phase readings
        # Calculate non-charging load per phase
        base_load_l1 = current_l1 - charge_l1
        base_load_l2 = current_l2 - charge_l2
        base_load_l3 = current_l3 - charge_l3
        
        # Find the highest loaded phase
        max_base_load = max(base_load_l1, base_load_l2, base_load_l3)
        
        # Get number of active charging phases directly from Zaptec data
        active_phases = int(zpdata.get("ActivePhases", 3))  # Default to 1 if not availabl
            
        # Calculate available capacity based on the most loaded phase
        current_threshold = float(config["current-threshold"])
        if(sum(sorted([int(charge_l1), int(charge_l2), int(charge_l3)])[0:2]) > 0):
            charging_budget_amps = int((current_threshold - max_base_load)*sqrt(3))
        else: 
            ic("1 phase charging")
            charging_budget_amps = int((current_threshold - max_base_load)*sqrt(3))
            #charging_budget_amps = int((current_threshold - max_base_load))
        
        ic("Base loads", base_load_l1, base_load_l2, base_load_l3)
        ic("Max base load", max_base_load)
        ic("Active phases", active_phases)
        ic("Calculated amps before sanitizing", charging_budget_amps)
        
        charging_budget_amps = min(POWER_MAX_AMPS, charging_budget_amps)
        charging_budget_amps = max(POWER_MIN_AMPS, charging_budget_amps)

        ic("Adjusting amps to budget", charging_budget_amps)
        ic(zaptec.charger_set_amps(config["zaptec-charger-id"], zpauth, charging_budget_amps))
    else:
        ic("Phase current data missing. Setting charging_budget_amps to minimum value for failsafe")
        ic(zaptec.charger_set_amps(config["zaptec-charger-id"], zpauth, POWER_MIN_AMPS))
    time.sleep(60)
