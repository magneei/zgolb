# Zaptec Go Load Balancer (ZGoLB)

Simple tool to do load balancing of zaptec go charger using tibber pulse as Tibbers load balacing is unfortunately not working very well with smaller main fuses.

ts-extractor.py extracts data from tibber pulse and writes to influx db
charger-control.py controls the actual charger

Update config-example.yaml with real values and store as config.yaml 

## Setup

Fill in `config.yaml` (see above), then run:

    ./install.sh

This creates the `.venv` virtualenv, installs `requirements.txt`, and installs, enables and (re)starts the two systemd services from `systemd/`. The unit files assume the repo is at `/home/magne/src/zgolb` and run as user `magne`; edit them if that differs. Re-run it after pulling changes or upgrading Python.

Logs: `journalctl -u zgolb-ts-extractor -f` / `journalctl -u zgolb-charger-control -f`
