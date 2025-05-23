#!/bin/bash

chmod +x tops_lab_install.sh &&chmod +x install.sh

sleep 2
./tops_lab_install.sh 
sleep 2

mkdir /usr/local/lib/custom
mv requirements.txt /usr/local/lib/custom/ &&mv aws-cred.py /usr/local/lib/custom/ && mv f5xc-eph-account.py /usr/local/lib/custom/

sleep 2
chown ubuntu:ubuntu /usr/local/lib/custom/requirements.txt
sleep 2
apt-get install -y python3-venv
python3 -m venv /usr/local/lib/custom/.venv &&source /usr/local/lib/custom/.venv/bin/activate &&pip3 install -r /usr/local/lib/custom/requirements.txt
sleep 2
pip3 install retry
sleep 2
mv f5xc-eph-account.service /etc/systemd/system/
useradd -r -s /bin/false f5xc-service
sleep 5
python3 -m venv /usr/local/lib/custom/.venv --system-site-packages
source /usr/local/lib/custom/.venv/bin/activate
pip install systemd-python
systemctl daemon-reload &&systemctl start f5xc-eph-account.service &&systemctl enable f5xc-eph-account.service
