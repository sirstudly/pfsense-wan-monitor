pfsense-wan-monitor
===================

A Python script designed to monitor the pfSense gateways by periodically checking gateway statuses. It identifies packet loss for specified WAN connections and executes configured commands to restart or renew DHCP when packet loss exceeds specified thresholds.

## Features

- Monitors multiple WAN connections at configurable intervals.
- Detects packet loss and issues warnings if loss exceeds defined thresholds.
- Automatically executes custom commands to restart a WAN or renew DHCP when necessary.
- Logs activity to a rotating log file for easy troubleshooting.

Usage
-----

To install the script, run this one-line command, which downloads the install script from Github and executes it with sh:

```
  fetch -o - https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/install-wanmonitor.sh | sh -s
```

Configuration
---------------------

Update `/usr/local/wanmonitor/wanmonitor.ini` with the correct commands to restart interfaces and to renew DHCP leases.
You can also configure the polling interval and the packet loss thresholds to hit before resetting the connection.

Starting and Stopping
---------------------

To start and stop the controller, use the `service` command from the command line.

- To start the wanmonitor:

  ```
    service wanmonitor.sh start
  ```
  The 'start' command exits immediately while the startup continues in the background.

- To stop the wanmonitor:

  ```
    service wanmonitor.sh stop
  ```
