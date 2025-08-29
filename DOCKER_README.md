# Docker Setup for pfSense WAN Monitor

This directory contains Docker configuration files to run the pfSense WAN Monitor in a containerized environment using Alpine Linux.

## Prerequisites

- Docker and Docker Compose installed on your system
- Network access to the pfSense system
- Smart plug IP addresses configured

## Quick Start

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f wan-monitor
   ```

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

## Configuration

### wanmonitor.ini
The `wanmonitor.ini` file is mounted from your local filesystem into the container. Make sure it's properly configured with:

- WAN interface names
- Loss thresholds
- Restart commands
- DHCP renewal commands

### Volume Mounts

- `./wanmonitor.ini` → `/app/wanmonitor.ini` (read-only)
- `./logs` → `/app/logs` (read-write for log persistence)
- `./gateway_status.txt` → `/app/gateway_status.txt` (read-only, if exists)

## Testing Smart Plug Functionality

Use the provided test script to test smart plug connectivity:

```bash
# Set environment variables (recommended)
export TAPO_USERNAME="your-tapo-email@example.com"
export TAPO_PASSWORD="your-tapo-password"

# Check plug status
./test_smart_plug.sh 192.168.1.100 status

# Turn plug on
./test_smart_plug.sh 192.168.1.100 on

# Turn plug off
./test_smart_plug.sh 192.168.1.100 off

# Restart plug (off for 10 seconds, then on)
./test_smart_plug.sh 192.168.1.100 restart

# Check power usage
./test_smart_plug.sh 192.168.1.100 power

# Or provide credentials as arguments
./test_smart_plug.sh 192.168.1.100 status myemail@example.com mypassword
```

## Container Management

### View running containers:
```bash
docker ps
```

### Access container shell:
```bash
docker exec -it pfsense-wan-monitor /bin/bash
```

### View container logs:
```bash
docker logs pfsense-wan-monitor
```

### Restart container:
```bash
docker-compose restart wan-monitor
```

## Troubleshooting

### Container won't start
- Check if the `wanmonitor.ini` file exists and is properly formatted
- Verify Docker has sufficient resources allocated
- Check Docker logs: `docker-compose logs wan-monitor`

### Smart plug connectivity issues
- Verify the plug IP address is correct and reachable from the container
- Test network connectivity: `docker exec pfsense-wan-monitor ping <plug_ip>`
- Ensure Tapo username and password are correct
- Check if the plug is properly set up in the Tapo app
- Verify the plug supports the P110 protocol

### pfSense connectivity issues
- Ensure the container can reach the pfSense system
- Verify the pfSsh.php command path is correct
- Check if SSH/API access is properly configured on pfSense

## Development

### Rebuild container after code changes:
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Run in development mode (with logs):
```bash
docker-compose up
```

## Security Notes

- The container runs as root (required for pfSense integration)
- Ensure proper network isolation in production
- Consider using Docker secrets for sensitive configuration
- Review and secure the restart commands in `wanmonitor.ini`
