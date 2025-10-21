
# Raspberry Pi Telemetry to Azure IoT Hub

This project sends CPU usage and temperature telemetry from a Raspberry Pi Zero 2 W to Azure IoT Hub using Python.
It demonstrates how to establish a lightweight, always-on IoT data pipeline for monitoring system health.

⸻

## Features
	•	Real-time telemetry every 60 seconds
	•	Secure connection using Azure IoT SDK
	•	Compatible with any Raspberry Pi model

⸻

## Requirements

pip install azure-iot-device psutil python-dotenv


⸻

## Run the Script

python send_to_iothub.py


⸻

## Optional: Run in Background

nohup python send_to_iothub.py &


⸻

## Notes
	•	Telemetry includes:
	•	cpu_percent
	•	temperature_celsius
	•	timestamp (UTC, ISO 8601 format)
	•	Ideal for learning Azure IoT end-to-end data flow
	•	Works perfectly with the Azure CLI monitoring command:

az iot hub monitor-events --hub-name <your-hub-name> --output table


⸻

## Future Improvements
	•	Add MQTT integration (e.g., AllThingsTalk or Mosquitto)
	•	Push telemetry to Azure Data Explorer or Microsoft Fabric
	•	Create a Power BI dashboard for visualization

⸻

Author: Omar Cruz
License: MIT

⸻
