#!/bin/sh

/usr/bin/fetch -o /usr/local/etc/rc.d/wanmonitor.sh ${FIXME-wanmonitor.sh}

# Fix permissions so it'll run
chmod +x /usr/local/etc/rc.d/wanmonitor.sh

# Add the startup variable to rc.conf.local.
# In the following comparison, we expect the 'or' operator to short-circuit, to make sure the file exists and avoid grep throwing an error.
if [ ! -f /etc/rc.conf.local ] || [ $(grep -c wanmonitor_enable /etc/rc.conf.local) -eq 0 ]; then
  echo -n "Enabling the wanmonitor service..."
  echo "wanmonitor_enable=YES" >> /etc/rc.conf.local
  echo " done."
fi
