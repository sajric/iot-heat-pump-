import math
import random
import zlib
from datetime import datetime


class TemperatureSimulator:
    """Generate a room's temperature with one wall-clock second per simulated minute."""

    def __init__(self, current_time, room_name="room"):
        self.start_time = current_time
        self.previous_time = current_time
        room_offset = (zlib.crc32(room_name.encode("utf-8")) % 151) / 100 - 0.75
        self.room_temp = 20 + room_offset

    @staticmethod
    def _ambient_temperature(sim_time):
        if sim_time.month in (12, 1, 2):
            seasonal_baseline = 18
        elif sim_time.month in (6, 7, 8):
            seasonal_baseline = 23
        else:
            seasonal_baseline = 20

        daily_variation = 1.5 * math.sin((sim_time.hour - 6) * math.pi / 12)
        return seasonal_baseline + daily_variation

    def get_temperature(self, current_date, dev_status):
        elapsed_seconds = max(0, (current_date - self.previous_time).total_seconds())
        self.previous_time = current_date

        elapsed_simulated_minutes = elapsed_seconds
        simulated_time = datetime.fromtimestamp(
            self.start_time.timestamp()
            + (current_date - self.start_time).total_seconds() * 60
        )

        ambient = self._ambient_temperature(simulated_time)
        target = 22.5 if dev_status == 1 else ambient
        response = min(elapsed_simulated_minutes / 180, 1)
        self.room_temp += (target - self.room_temp) * response
        self.room_temp = min(30, max(10, self.room_temp))

        measured_temperature = self.room_temp + random.uniform(-0.08, 0.08)
        return simulated_time, round(measured_temperature, 2)
