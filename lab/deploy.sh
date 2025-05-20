#!/bin/bash

set -e  # Exit immediately on error

echo "➤ Step 1: Make install scripts executable"
chmod +x tops_lab_install.sh install.sh

# --------------------------------------------------------------------

echo "➤ Step 2: Run lab install script"
./tops_lab_install.sh
sleep 1

# --------------------------------------------------------------------

echo "➤ Step 3: Move source files to custom directory"
mkdir -p /usr/local/lib/custom
mv requirements.txt aws-cred.py f5xc-eph-account.py /usr/local/lib/custom/

# Set correct ownership
chown ubuntu:ubuntu /usr/local/lib/custom/requirements.txt

# --------------------------------------------------------------------

echo "➤ Step 4: Install Python venv and create virtual environment"
apt-get update && apt-get install -y python3-venv

# Initial venv setup
python3 -m venv /usr/local/lib/custom/.venv

# Activate venv and install Python dependencies
source /usr/local/lib/custom/.venv/bin/activate
pip install -r /usr/local/lib/custom/requirements.txt
pip install retry  # Manual install if not in requirements.txt

# --------------------------------------------------------------------

echo "➤ Step 5: Move systemd service and create service user"
mv f5xc-eph-account.service /etc/systemd/system/

# Create a dedicated system user (no login)
useradd -r -s /bin/false f5xc-service

# --------------------------------------------------------------------

echo "➤ Step 6: Recreate venv with system packages (for systemd-python)"
# This ensures access to system-level Python packages like `libsystemd`
python3 -m venv /usr/local/lib/custom/.venv --system-site-packages

# Re-activate and install systemd-python
source /usr/local/lib/custom/.venv/bin/activate
pip install systemd-python

# --------------------------------------------------------------------

echo "➤ Step 7: Reload systemd and start the service"
systemctl daemon-reload
systemctl start f5xc-eph-account.service
systemctl enable f5xc-eph-account.service

echo "✅ Done. Service installed and started."
