#!/bin/sh

if [ -z "$1" ]; then
  echo "Missing argument: interface to be reset. eg. opt4"
else
  # See https://forum.netgate.com/topic/188031/cli-how-to-release-renew-wan-dhcp-one-solution/3
  /usr/local/bin/php -r "require 'interfaces.inc'; interface_configure('$1',TRUE,TRUE);"
fi
