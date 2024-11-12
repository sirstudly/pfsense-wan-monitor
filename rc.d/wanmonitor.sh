#!/bin/sh

# REQUIRE: FILESYSTEMS
# REQUIRE: NETWORKING
# PROVIDE: wanmonitor

. /etc/rc.subr

name="wanmonitor"
rcvar="wanmonitor_enable"
start_cmd="wanmonitor_start"
stop_cmd="wanmonitor_stop"

pidfile="/var/run/${name}.pid"

load_rc_config ${name}

wanmonitor_start()
{
  if checkyesno ${rcvar}; then
    echo "Starting Wan Monitor. "

    # The process will run until it is terminated and does not fork on its own.
    # So we start it in the background and stash the pid:
    cd /usr/local/wanmonitor
    /usr/local/bin/python3.11 wanmonitor.py &
    echo $! > $pidfile

  fi
}

wanmonitor_stop()
{

  if [ -f $pidfile ]; then
    echo -n "Stopping Wan Monitor..."

    kill `pgrep -F $pidfile`

    # Remove the pid file:
    rm $pidfile

    echo " stopped.";
  else
    echo "There is no pid file. The process may not be running."
  fi
}

run_rc_command "$1"