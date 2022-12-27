# zgolb

Simple tool to do load balancing of zaptec go charger using tibber pulse as Tibbers load balacing is unfortunately not working very well with smaller main fuses.

ts-extractor.py extracts data from tibber pulse and writes to influx db
charger-control.py controls the actual charger

Update config-example.yaml with real values and store as config.yaml 
