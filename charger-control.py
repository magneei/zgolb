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

    if "TotalChargePower" in zpdata:
        tsdb.insert_ts("zaptec", "chargepower", float(zpdata["TotalChargePower"]))

    if avg_power:
        if avg_power > config["power-threshold"]:
            ic("Power over threshold")

        charging_budget = float(config["power-threshold"]) - avg_power + avg_charge

        # amps calculated for IT real 3 phase charging
        charging_budget_amps = int(charging_budget / 230 / sqrt(3))
        ic("Calculated amps before sanitizing", charging_budget_amps)
        charging_budget_amps = min(POWER_MAX_AMPS, charging_budget_amps)
        charging_budget_amps = max(POWER_MIN_AMPS, charging_budget_amps)

        # Amps are adjusted regardless of charging status, which is a bit noisy
        ic("Adjusting amps to budget", charging_budget_amps)
        ic(
            zaptec.charger_set_amps(
                config["zaptec-charger-id"], zpauth, charging_budget_amps
            )
        )
    else:
        ic(
            "avg_power data missing. Setting charging_budget_amps to minimum value for failsafe"
        )
        ic(zaptec.charger_set_amps(config["zaptec-charger-id"], zpauth, POWER_MIN_AMPS))
    time.sleep(60)
