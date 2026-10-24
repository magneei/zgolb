#!/usr/bin/env bash
# Set up the virtualenv and install/enable the ZGoLB systemd services.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f config.yaml ]; then
    echo "config.yaml missing - copy config-example.yaml and fill in real values first" >&2
    exit 1
fi

[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

sudo cp systemd/zgolb-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable zgolb-ts-extractor zgolb-charger-control
sudo systemctl restart zgolb-ts-extractor zgolb-charger-control

systemctl --no-pager status zgolb-ts-extractor zgolb-charger-control | grep -E "●|Active:"
