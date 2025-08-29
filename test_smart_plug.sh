#!/bin/bash

# Test script for smart plug functionality
# Usage: ./test_smart_plug.sh <plug_ip> <action> [username] [password]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <plug_ip> <action> [username] [password]"
    echo "Actions: status, on, off, restart, power"
    echo "Example: $0 192.168.1.100 status myemail@example.com mypassword"
    echo ""
    echo "Environment variables TAPO_USERNAME and TAPO_PASSWORD can also be used."
    exit 1
fi

PLUG_IP=$1
ACTION=$2
TAPO_USERNAME=${3:-$TAPO_USERNAME}
TAPO_PASSWORD=${4:-$TAPO_PASSWORD}

# Check if credentials are provided
if [ -z "$TAPO_USERNAME" ] || [ -z "$TAPO_PASSWORD" ]; then
    echo "Error: Tapo username and password are required."
    echo "Provide them as arguments or set TAPO_USERNAME and TAPO_PASSWORD environment variables."
    exit 1
fi

echo "Testing smart plug at $PLUG_IP with action: $ACTION"

# Run the smart plug script inside the container
docker exec pfsense-wan-monitor python tapo_smart_plug.py --host $PLUG_IP --username $TAPO_USERNAME --password $TAPO_PASSWORD --action $ACTION

echo "Test completed."
