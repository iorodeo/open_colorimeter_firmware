import busio
import board
import adafruit_tsl2591

TSL2591_MAX_COUNT_100MS = 36863  # 0x8FFF
TSL2591_MAX_COUNT = 65535        # 0xFFFF

class LightSensor:

    def __init__(self):

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self._device = adafruit_tsl2591.TSL2591(i2c)
        self.gain = adafruit_tsl2591.GAIN_MED
        self.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
        self.channel = 0

    @property
    def max_counts(self):
        if self.integration_time == adafruit_tsl2591.INTEGRATIONTIME_100MS:
            return TSL2591_MAX_COUNT_100MS 
        else:
            return TSL2591_MAX_COUNT 

    @property
    def value(self):
        value = self._device.raw_luminosity[self.channel]
        if value >= self.max_counts:
            raise LightSensorOverflow('light sensor reading > max_counts')
        return float(value)

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value
        self._device.gain = value

    @property
    def integration_time(self):
        return self._integration_time

    @integration_time.setter
    def integration_time(self, value):
        self._integration_time = value
        self._device.integration_time = value


class LightSensorOverflow(Exception):
    pass
