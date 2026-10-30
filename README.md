# IoT Heat Pump Simulation

The Docker Compose stack runs a Mosquitto MQTT broker, five simulated room
temperature sensors, and a gateway/ingestor. Simulated time advances at a
1:60 ratio: one real second advances the sensor's simulated clock by one minute.

## Temperature sensors

Each sensor has an independent `TemperatureSimulator` instance. It starts at a
slightly room-specific temperature, moves gradually toward a seasonal and
time-of-day ambient temperature when the heat pump is off, and toward a heating
setpoint when it is on. A small measurement variation makes consecutive
readings realistic without producing implausible outliers.

The sensor publishes JSON to `<room>/temperature`:

```json
{"timestamp": "2026-10-29T15:33:11", "value": 20.12}
```

The sensor listens on `<room>/heatpump` for JSON status commands:

```json
{"status": 1}
```

Status `1` means on and `0` means off. The included rooms are `room1`, `room2`,
`room3`, `living_room`, and `office`.

## Gateway / ingestor

The gateway subscribes to `+/temperature` and `+/heatpump`. It validates each
payload and writes a normalized JSON record to its container log, ready for a
downstream consumer such as Kafka. Malformed messages are logged and discarded.
Kafka is not part of this Compose stack.

## Run

From the project directory, start the broker, sensors, and gateway with:

```sh
docker compose up --build
```

The services connect over the Compose `internal_net` network using the broker
hostname `mosquitto`. Port 1883 is also published on the host for development
clients. The broker allows anonymous access for this local simulation; add
authentication before exposing it beyond a trusted development environment.
