#!/bin/bash

# Setup the variables
source ~/.bashrc

# Sync the repo
git pull

# Check if libwasmvm.so is installed
if [ ! -f "/lib/libwasmvm.so" ]; then
    wget -O /lib/libwasmvm.so https://github.com/CosmWasm/wasmvm/raw/main/api/libwasmvm.so
fi

systemctl stop validator.target umee.service
systemctl disable validator.target umee.service
cp Services/validator.target /etc/systemd/system/validator.target
cp Services/validator@.service /etc/systemd/system/validator@.service
cp Services/umee.service /etc/systemd/system/umee.service


systemctl daemon-reload
systemctl enable validator.target umee.service

# Run the bots
systemctl restart validator.target umee.service