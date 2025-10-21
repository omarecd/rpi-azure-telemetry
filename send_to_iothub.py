import os
import psutil
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message

# Load connection string from .env
load_dotenv()
conn_str = os.getenv("IOTHUB_CONNECTION_STRING")

# Initialize IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(conn_str)

print("✅ Connected to Azure IoT Hub. Sending telemetry...")

try:
    while True:
        # Collect telemetry
        cpu = psutil.cpu_percent()
        temps = psutil.sensors_temperatures()
        temp = temps["cpu_thermal"][0].current if "cpu_thermal" in temps else 0.0
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Build message payload
        data = {
            "timestamp": timestamp,
            "cpu_percent": cpu,
            "temperature_celsius": temp
        }

        # Send message to IoT Hub
        message = Message(str(data))
        client.send_message(message)
        print(f"→ Sent: {data}")

        time.sleep(60)  # Send every 60 seconds

except KeyboardInterrupt:
    print("\n🛑 Stopping telemetry...")
finally:
    client.shutdown()
    print("🔌 Disconnected from Azure IoT Hub.")
