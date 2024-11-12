import subprocess
import time
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler

# Global configuration variables
WAN_NAMES = []
INTERVAL = 60
LOSS_THRESHOLD = 50.0
CONSECUTIVE_CHECKS = 3
LOG_FILE = "wanmonitor.log"
LOGGER = logging.getLogger("WANMonitor")
LOSS_COUNTS = []
LOSS_100_COUNTS = []
RESTART_WAN_COMMANDS = []
RENEW_DHCP_COMMANDS = []


# Load configurations function
def load_config():
    global WAN_NAMES, INTERVAL, LOSS_THRESHOLD, CONSECUTIVE_CHECKS, LOG_FILE, LOGGER, LOSS_COUNTS, LOSS_100_COUNTS, RESTART_WAN_COMMANDS, RENEW_DHCP_COMMANDS
    config = configparser.ConfigParser()
    config.read('wanmonitor.ini')

    WAN_NAMES = config['Settings'].get('wan_names').split(',')
    INTERVAL = config['Settings'].getint('interval_seconds', INTERVAL)
    LOSS_THRESHOLD = config['Settings'].getfloat('loss_threshold', LOSS_THRESHOLD)
    CONSECUTIVE_CHECKS = config['Settings'].getint('consecutive_checks', CONSECUTIVE_CHECKS)
    LOG_FILE = config['Settings'].get('log_file', LOG_FILE)

    # Track consecutive losses and 100% loss counts for each WAN
    LOSS_COUNTS = {wan_name.strip(): 0 for wan_name in WAN_NAMES}
    LOSS_100_COUNTS = {wan_name.strip(): 0 for wan_name in WAN_NAMES}
    RESTART_WAN_COMMANDS = {wan_name.strip(): config[wan_name.strip()].get('restart_wan_command') if wan_name.strip() in config else f"echo 'restart_wan_command[{wan_name.strip()}] is not configured!" for wan_name in WAN_NAMES}
    RENEW_DHCP_COMMANDS = {wan_name.strip(): config[wan_name.strip()].get('renew_dhcp_command') if wan_name.strip() in config else f"echo 'renew_dhcp_command[{wan_name.strip()}] is not configured!" for wan_name in WAN_NAMES}

    # Logging setup
    LOGGER.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=7)
    handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)


def parse_gatewaystatus_output(output):
    """
    Parses the output of the `pfSsh.php playback gatewaystatus` command and returns a dictionary.
    """
    lines = output.splitlines()
    for line in lines[1:]:  # Skip header line
        columns = line.split()
        if len(columns) < 7:
            continue  # Skip any malformed lines
        name, _, _, _, _, loss, status, *_ = columns
        loss = float(loss.strip('%'))
        yield name, loss, status


def check_wan_status():
    """
    Executes the gateway status command and checks for packet loss on each specified WAN.
    """
    try:
        result = subprocess.run(['pfSsh.php', 'playback', 'gatewaystatus'],
                                capture_output=True, text=True, check=True)
        LOGGER.debug("Gateway status output:\n" + result.stdout)
        wan_status = {name: (loss, status) for name, loss, status in parse_gatewaystatus_output(result.stdout)}

        for wan_name in LOSS_COUNTS.keys():
            if wan_name in wan_status:
                current_loss, current_status = wan_status[wan_name]
                LOGGER.info(f"Current packet loss for {wan_name}: {current_loss}% (Status: {current_status})")

                # Only increment loss count if loss is above threshold
                if current_loss > LOSS_THRESHOLD:
                    if current_loss == 100.0:
                        LOSS_100_COUNTS[wan_name] += 1
                    else:
                        LOSS_100_COUNTS[wan_name] = 0  # Reset 100% loss count if loss is not 100%

                    LOSS_COUNTS[wan_name] += 1
                    LOGGER.warning(f"{wan_name} packet loss exceeded threshold with status '{current_status}'! "
                                   f"Count: {LOSS_COUNTS[wan_name]}/{CONSECUTIVE_CHECKS}")
                else:  # Reset loss counts if loss is below threshold
                    LOSS_COUNTS[wan_name] = 0
                    LOSS_100_COUNTS[wan_name] = 0

                # If 100% loss count reached consecutive threshold, reset interface
                if LOSS_100_COUNTS[wan_name] >= CONSECUTIVE_CHECKS:
                    release_renew_dhcp(wan_name)
                    LOSS_100_COUNTS[wan_name] = 0  # Reset after action
                    LOSS_COUNTS[wan_name] = 0
                # If loss exceeded threshold for consecutive checks, restart WAN device
                elif LOSS_COUNTS[wan_name] >= CONSECUTIVE_CHECKS:
                    restart_wan(wan_name)
                    LOSS_100_COUNTS[wan_name] = 0  # Reset after action
                    LOSS_COUNTS[wan_name] = 0  # Reset after action
            else:
                LOGGER.error(f"WAN '{wan_name}' not found in gateway status output.")
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Error executing gateway status command: {e}")


def restart_wan(wan_name):
    """
    Executes the restart command for a specific WAN and logs its output.
    """
    try:
        result = subprocess.run(f"{RESTART_WAN_COMMANDS[wan_name]}", shell=True, capture_output=True, text=True, check=True)
        LOGGER.info(f"Restart command output for {wan_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Restart command for {wan_name} failed with error: {e.returncode}\n{e.stderr}")


def release_renew_dhcp(wan_name):
    """
    Executes the release and renew DHCP command for a specific WAN and logs its output.
    """
    try:
        result = subprocess.run(f"{RENEW_DHCP_COMMANDS[wan_name]}", shell=True, capture_output=True, text=True, check=True)
        LOGGER.info(f"Release/Renew DHCP command output for {wan_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Release/Renew DHCP command for {wan_name} failed with error: {e.returncode}\n{e.stderr}")


def main():
    """
    Main loop for monitoring the WAN status.
    """
    LOGGER.info("Starting WAN Monitor...")
    load_config()
    while True:
        check_wan_status()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()