"""
Tapo Smart Plug Controller for WAN Monitor
Controls TP-Link Tapo smart plugs (P110, P100, P105, etc.) for WAN restart operations
"""

import asyncio
import sys
import logging
from typing import Optional
import argparse

try:
    from tapo import ApiClient
except ImportError:
    print("Error: tapo module not found. Install with: pip install tapo")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_plug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TapoSmartPlugController:
    def __init__(self, host: str, username: str, password: str):
        """
        Initialize the Tapo smart plug controller.

        Args:
            host: IP address of the smart plug
            username: Tapo username/email
            password: Tapo password
        """
        self.host = host
        self.username = username
        self.password = password
        self.client = ApiClient(username, password)
        self.device = None

    def _log_device_info(self, device_info: object, context: str = ""):
        """
        Common function to log device info in a consistent format.
        
        Args:
            device_info: The device info object from the Tapo API
            context: Optional context string to include in the log
        """
        context_str = f" ({context})" if context else ""
        logger.info(f"Device info for Tapo P110 at {self.host}{context_str}:")
        logger.info(f"  Object type: {type(device_info)}")
        logger.info(f"  Object repr: {repr(device_info)}")

        # Try to get all attributes
        try:
            for attr in dir(device_info):
                if not attr.startswith('_'):  # Skip private attributes
                    try:
                        value = getattr(device_info, attr)
                        if not callable(value):  # Skip methods
                            logger.info(f"  {attr}: {value}")
                    except Exception as attr_e:
                        logger.info(f"  {attr}: <error accessing: {attr_e}>")
        except Exception as dir_e:
            logger.info(f"  Error listing attributes: {dir_e}")

    async def connect(self):
        """Establish connection to the smart plug."""
        try:
            # Create P110 device instance
            self.device = await self.client.p110(self.host)
            
            # Test connection by getting device info
            device_info = await self.device.get_device_info()
            logger.info(f"Successfully connected to Tapo P110 at {self.host}")
            logger.info(f"Device info: {device_info}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tapo P110 at {self.host}: {e}")
            return False

    async def get_status(self):
        """Get the current status of the smart plug."""
        try:
            if not self.device:
                logger.error("Device not connected. Call connect() first.")
                return None
            
            device_info = await self.device.get_device_info()

            # Log the entire device info object to see all available data
            self._log_device_info(device_info, "status check")

            is_on = device_info.device_on
            logger.info(f"Tapo P110 at {self.host} is {'ON' if is_on else 'OFF'}")
            return is_on
        except Exception as e:
            logger.error(f"Failed to get status from Tapo P110 at {self.host}: {e}")
            return None

    async def turn_on(self):
        """Turn on the smart plug."""
        try:
            if not self.device:
                logger.error("Device not connected. Call connect() first.")
                return False

            await self.device.on()
            logger.info(f"Turned ON Tapo P110 at {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to turn ON Tapo P110 at {self.host}: {e}")
            return False

    async def turn_off(self):
        """Turn off the smart plug."""
        try:
            if not self.device:
                logger.error("Device not connected. Call connect() first.")
                return False

            await self.device.off()
            logger.info(f"Turned OFF Tapo P110 at {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to turn OFF Tapo P110 at {self.host}: {e}")
            return False

    async def restart(self, delay_seconds: int = 10):
        """
        Restart the smart plug by turning it off, waiting, then turning it on.

        Args:
            delay_seconds: Number of seconds to wait between off and on
        """
        try:
            logger.info(f"Starting restart sequence for Tapo P110 at {self.host}")

            # Turn off
            if not await self.turn_off():
                return False

            # Wait
            logger.info(f"Waiting {delay_seconds} seconds before turning back on...")
            await asyncio.sleep(delay_seconds)

            # Turn on
            if not await self.turn_on():
                return False

            # Wait again and check if device is still ON
            logger.info(f"Waiting {delay_seconds} seconds to check device state...")
            await asyncio.sleep(delay_seconds)
            
            # Check current state
            current_status = await self.get_status()
            if not current_status:  # Device is still OFF
                logger.info(f"Device is still OFF, calling turn_on again for Tapo P110 at {self.host}")
                return await self.turn_on()
            else:  # Device is ON
                logger.info(f"Device state check completed for Tapo P110 at {self.host}")

            logger.info(f"Successfully restarted Tapo P110 at {self.host}")
            return True

        except Exception as e:
            logger.error(f"Failed to restart Tapo P110 at {self.host}: {e}")
            return False

    async def get_power_usage(self):
        """Get current power usage (if supported by the device)."""
        try:
            if not self.device:
                logger.error("Device not connected. Call connect() first.")
                return None

            power_usage = await self.device.get_current_power()
            logger.info(f"Current power usage for Tapo P110 at {self.host}: {power_usage}")
            return power_usage
        except Exception as e:
            logger.error(f"Failed to get power usage from Tapo P110 at {self.host}: {e}")
            return None


async def main():
    """Main function to handle command line operations."""
    parser = argparse.ArgumentParser(description='Control TP-Link Tapo smart plugs')
    parser.add_argument('--host', required=True, help='IP address of the smart plug')
    parser.add_argument('--username', required=True, help='Tapo username/email')
    parser.add_argument('--password', required=True, help='Tapo password')
    parser.add_argument('--action', required=True, choices=['status', 'on', 'off', 'restart', 'power'],
                        help='Action to perform')
    parser.add_argument('--delay', type=int, default=10,
                        help='Delay in seconds for restart operation (default: 10)')

    args = parser.parse_args()

    # Create controller
    controller = TapoSmartPlugController(args.host, args.username, args.password)

    # Connect
    if not await controller.connect():
        sys.exit(1)

    # Perform action
    success = False
    if args.action == 'status':
        status = await controller.get_status()
        success = status is not None
    elif args.action == 'on':
        success = await controller.turn_on()
    elif args.action == 'off':
        success = await controller.turn_off()
    elif args.action == 'restart':
        success = await controller.restart(args.delay)
    elif args.action == 'power':
        power_usage = await controller.get_power_usage()
        success = power_usage is not None

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())