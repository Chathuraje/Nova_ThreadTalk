#!/bin/bash

# Stop services
sudo systemctl stop nova_threadtalk.service
sudo systemctl stop nova_threadtalk_dev.service

# Copy service files
sudo cp nova_threadtalk.service /etc/systemd/system/
sudo cp nova_threadtalk_dev.service /etc/systemd/system/

# Reload systemctl daemon
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable nova_threadtalk.service
sudo systemctl enable nova_threadtalk_dev.service

# Start services
sudo systemctl start nova_threadtalk.service
sudo systemctl start nova_threadtalk_dev.service

echo "Setup completed."
