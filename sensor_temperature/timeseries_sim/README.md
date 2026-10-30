# SIMULATION OF TIMESERIES

This library provides a simulation tool to get data from temperature and presence sensors:

You must initiate the simulator with a base timestamp. The simulator returns
temperature and presence values with a simulated timestamp. For temperature
sensors, one real-world second advances simulated time by one minute (1:60).

Simulator classes:
TemperatureSimulator(<current datetime>)
    - get_temperature(<current datetime>, <heatpump status>)
PresenceSimulator(<current datetime>)
    - get_presence(<current datetime>)

Usage:
```python
from timeseries_get import TemperatureSimulator, PresenceSimulator
from datetime import datetime
# Initialize the simulators with the current time
ts = TemperatureSimulator(datetime.now())
ps = PresenceSimulator(datetime.now())

# get the simulated time and value from the object
print(ts.get_temperature(datetime.now(), 1))
print(ps.get_presence(datetime.now()))

```
