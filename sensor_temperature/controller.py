import os
import json
import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from timeseries_get import TemperatureSimulator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
sensor_topic_status = os.environ["SENSOR_TOPIC_STATUS"]
sensor_topic_data = os.environ["SENSOR_TOPIC_DATA"]
mqtt_host = os.environ.get("MQTT_HOST", "mosquitto")
room_name = os.environ.get("SENSOR_ROOM", sensor_topic_data.removesuffix("/temperature"))
heatpump = {"status": 0}


def heatpump_status_change(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        status = payload["status"]
        if isinstance(status, bool) or status not in (0, 1, "0", "1"):
            raise ValueError("status must be 0 (off) or 1 (on)")
        heatpump["status"] = int(status)
        logging.info("Heat pump status changed to %s", heatpump["status"])
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        logging.warning("Ignoring invalid status on %s: %s", message.topic, error)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        logging.error("MQTT connection to %s failed with code %s", mqtt_host, rc)
        return
    logging.info("Connected to MQTT broker at %s", mqtt_host)
    client.subscribe(sensor_topic_status, qos=1)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = heatpump_status_change
client.connect_async(mqtt_host, 1883, 60)
client.loop_start()

temperature_simulator = TemperatureSimulator(datetime.now(), room_name)

try:
    while True:
        if client.is_connected():
            simulated_time, temperature = temperature_simulator.get_temperature(
                datetime.now(), heatpump["status"]
            )
            payload = json.dumps(
                {"timestamp": simulated_time.isoformat(), "value": temperature}
            )
            result = client.publish(sensor_topic_data, payload, qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logging.warning("Could not publish reading to %s", sensor_topic_data)
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Stopping temperature sensor")
finally:
    client.loop_stop()
    client.disconnect()


