"""
send_to_iothub_twin.py
----------------------

Enhanced version of the telemetry script for Raspberry Pi Zero 2 W.
This script sends CPU and temperature telemetry to Azure IoT Hub and
supports dynamic configuration using the Device Twin (desired/reported properties).

Key features:
Reads telemetry interval from the IoT Hub Device Twin (default: 60s)
Listens for Twin updates in real time
Reports back applied settings and device state
Sends periodic telemetry data to Azure IoT Hub
"""

import os
import psutil
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message

# -----------------------------------------------------------------------------
# 1 - Load connection string and initialize IoT Hub client
# -----------------------------------------------------------------------------
load_dotenv()
conn_str = os.getenv("IOTHUB_CONNECTION_STRING")
if not conn_str:
    raise ValueError("Missing IOTHUB_CONNECTION_STRING in .env file.")

client = IoTHubDeviceClient.create_from_connection_string(conn_str)
print("Connected to Azure IoT Hub.")

# -----------------------------------------------------------------------------
# 2 - Define global configuration variable (default interval = 60 seconds)
# -----------------------------------------------------------------------------
telemetry_interval = 60  # This will be overridden if Twin specifies a value


# -----------------------------------------------------------------------------
# 3 - Define a function to handle Twin updates from Azure
# -----------------------------------------------------------------------------
def handle_twin_update(patch):
    """
    Called automatically when Azure updates the device's desired properties.
    Updates the local telemetry interval if present in the patch.
    """
    global telemetry_interval

    if "telemetry_interval" in patch:
        new_interval = patch["telemetry_interval"]
        telemetry_interval = new_interval
        print(f"Received Twin update → telemetry_interval = {telemetry_interval}s")

        # Report back to Azure that the new interval was applied successfully
        reported_patch = {"telemetry_interval": telemetry_interval}
        client.patch_twin_reported_properties(reported_patch)
        print(f"Reported applied interval: {reported_patch}")


# -----------------------------------------------------------------------------
# 4 - Retrieve initial Twin and set current interval
# -----------------------------------------------------------------------------
try:
    twin = client.get_twin()
    desired = twin.get("desired", {})
    telemetry_interval = desired.get("telemetry_interval", telemetry_interval)
    print(f"Using telemetry interval = {telemetry_interval}s (from Twin or default)")
except Exception as e:
    print(f"Could not read initial Twin: {e}")
    # Continue with default interval


# -----------------------------------------------------------------------------
# 5 - Subscribe to Twin updates so changes are applied dynamically
# -----------------------------------------------------------------------------
client.on_twin_desired_properties_patch_received = handle_twin_update


# -----------------------------------------------------------------------------
# 6 - Main telemetry loop
# -----------------------------------------------------------------------------
try:
    print("Starting telemetry loop... Press Ctrl+C to stop.\n")

    while True:
        # Gather telemetry
        cpu = psutil.cpu_percent()
        temps = psutil.sensors_temperatures()
        temp = temps["cpu_thermal"][0].current if "cpu_thermal" in temps else 0.0
        uptime = int(time.time() - psutil.boot_time())
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Create telemetry message
        data = {
            "timestamp": timestamp,
            "cpu_percent": cpu,
            "temperature_celsius": temp,
            "uptime_sec": uptime,
        }

        # Send telemetry to Azure IoT Hub
        message = Message(str(data))
        client.send_message(message)
        print(f"→ Sent: {data}")

        # Update Twin with last known values (latest snapshot)
        reported_properties = {
            "cpu_percent": cpu,
            "temperature_celsius": temp,
            "uptime_sec": uptime,
            "last_update_utc": timestamp,
        }
        client.patch_twin_reported_properties(reported_properties)

        # Wait based on current interval (updated dynamically by Twin)
        time.sleep(telemetry_interval)

except KeyboardInterrupt:
    print("\nTelemetry loop stopped by user.")

except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    client.shutdown()
    print("Disconnected from Azure IoT Hub.")
