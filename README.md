pfsense-wan-monitor
===================

A script that runs on pfSense monitoring selected gateways and attempts to fix them if they are offline or exhibit high packet loss.

Usage
-----

To install the script, run this one-line command, which downloads the install script from Github and executes it with sh:

```
  fetch -o - https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/install-wanmonitor.sh | sh -s
```

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
