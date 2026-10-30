import json
import logging
import math
import os
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
mqtt_host = os.environ.get("MQTT_HOST", "mosquitto")


def process_message(message):
    topic_parts = message.topic.split("/")
    if len(topic_parts) < 2 or not topic_parts[-2]:
        raise ValueError("topic must contain a room and event type")

    room = "/".join(topic_parts[:-1])
    event_type = topic_parts[-1]
    payload = json.loads(message.payload.decode("utf-8"))

    if event_type == "temperature":
        timestamp = payload["timestamp"]
        value = payload["value"]
        if not isinstance(timestamp, str) or not timestamp:
            raise ValueError("temperature timestamp must be a non-empty string")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("temperature value must be numeric")
        if not math.isfinite(value):
            raise ValueError("temperature value must be finite")
        record = {
            "room": room,
            "event_type": "temperature",
            "timestamp": timestamp,
            "value": float(value),
            "source_topic": message.topic,
        }
    elif event_type == "heatpump":
        status = payload["status"]
        if isinstance(status, bool) or status not in (0, 1, "0", "1"):
            raise ValueError("heat-pump status must be 0 (off) or 1 (on)")
        record = {
            "room": room,
            "event_type": "heatpump_status",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": int(status),
            "source_topic": message.topic,
        }
    else:
        raise ValueError("unsupported event type")

    return record


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        logging.error("MQTT connection to %s failed with code %s", mqtt_host, rc)
        return
    logging.info("Connected to MQTT broker at %s", mqtt_host)
    client.subscribe([("+/temperature", 1), ("+/heatpump", 1)])


def on_message(client, userdata, message):
    try:
        record = process_message(message)
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        logging.error("Discarding invalid MQTT message on %s: %s", message.topic, error)
        return

    logging.info("INGESTED %s", json.dumps(record, sort_keys=True))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect_async(mqtt_host, 1883, 60)
client.loop_forever()
