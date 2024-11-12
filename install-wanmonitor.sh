#!/bin/sh

/usr/bin/fetch -o /usr/local/etc/rc.d/wanmonitor.sh https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/rc.d/wanmonitor.sh

# Fix permissions so it'll run
chmod +x /usr/local/etc/rc.d/wanmonitor.sh

# Copy python script and config to /usr/local/wanmonitor
echo "Copying files..."
mkdir -p /usr/local/wanmonitor
/usr/bin/fetch -o /usr/local/wanmonitor/wanmonitor.py https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/wanmonitor.py
/usr/bin/fetch -o /usr/local/wanmonitor/wanmonitor.ini https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/wanmonitor.ini
/usr/bin/fetch -o /usr/local/wanmonitor/renew_dhcp.sh https://raw.githubusercontent.com/sirstudly/pfsense-wan-monitor/refs/heads/master/renew_dhcp.sh
chmod +x /usr/local/wanmonitor/renew_dhcp.sh
echo "Configure /usr/local/wanmonitor/wanmonitor.ini manually."

# Add the startup variable to rc.conf.local.
# In the following comparison, we expect the 'or' operator to short-circuit, to make sure the file exists and avoid grep throwing an error.
if [ ! -f /etc/rc.conf.local ] || [ $(grep -c wanmonitor_enable /etc/rc.conf.local) -eq 0 ]; then
  echo -n "Enabling the wanmonitor service..."
  echo "wanmonitor_enable=YES" >> /etc/rc.conf.local
  echo " done."
fi
