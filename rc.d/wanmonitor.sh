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
workdir="/usr/local/wanmonitor"
command="/usr/local/bin/python3.11 ${workdir}/wanmonitor.py"

load_rc_config ${name}

wanmonitor_start() {
  if checkyesno ${rcvar}; then
    echo "Starting Wan Monitor."

    # Check if the process is already running
    if [ -f "${pidfile}" ] && kill -0 "$(cat ${pidfile})" 2>/dev/null; then
      echo "${name} is already running as PID $(cat ${pidfile})."
      return 1
    fi

    # Start the process in the background and save its PID
    cd "${workdir}"
    ${command} &
    echo $! > ${pidfile}

    # Validate that the PID file was written and process is running
    if ! kill -0 "$(cat ${pidfile})" 2>/dev/null; then
      echo "Failed to start ${name}."
      rm -f ${pidfile}
      return 1
    fi

    echo "${name} started with PID $(cat ${pidfile})."
  fi
}

wanmonitor_stop() {
  if [ -f "${pidfile}" ]; then
    pid=$(cat ${pidfile})

    echo "Stopping Wan Monitor (PID ${pid})..."

    # Gracefully stop the process
    kill "${pid}" && wait "${pid}" 2>/dev/null

    # Remove the PID file
    rm -f "${pidfile}"

    echo "${name} stopped."
  else
    echo "No PID file found. ${name} may not be running."
  fi
}

run_rc_command "$1"