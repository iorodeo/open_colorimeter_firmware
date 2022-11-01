# ---
import time
# ----
import busio
import board
import adafruit_tsl2591


class LightSensor:

    TSL2591_MAX_COUNT_100MS = 36863  # 0x8FFF
    TSL2591_MAX_COUNT = 65535        # 0xFFFF

    GAIN_DICT = { 
            adafruit_tsl2591.GAIN_LOW  : 1.0,
            adafruit_tsl2591.GAIN_MED  : 25.0,
            adafruit_tsl2591.GAIN_HIGH : 428.0, 
            adafruit_tsl2591.GAIN_MAX  : 9876.0,
            }

    INTEGRATION_TIME_DICT = { 
            adafruit_tsl2591.INTEGRATIONTIME_100MS :  100.0,
            adafruit_tsl2591.INTEGRATIONTIME_200MS :  200.0,
            adafruit_tsl2591.INTEGRATIONTIME_300MS :  300.0,
            adafruit_tsl2591.INTEGRATIONTIME_400MS :  400.0,
            adafruit_tsl2591.INTEGRATIONTIME_500MS :  500.0,
            adafruit_tsl2591.INTEGRATIONTIME_600MS :  600.0,
            }

    MAX_COUNT_DICT = {
            adafruit_tsl2591.INTEGRATIONTIME_100MS : 36863,
            adafruit_tsl2591.INTEGRATIONTIME_200MS : 65535,
            adafruit_tsl2591.INTEGRATIONTIME_300MS : 65535,
            adafruit_tsl2591.INTEGRATIONTIME_400MS : 65535,
            adafruit_tsl2591.INTEGRATIONTIME_500MS : 65535,
            adafruit_tsl2591.INTEGRATIONTIME_600MS : 65535,
            }


    def __init__(self):

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self._device = adafruit_tsl2591.TSL2591(i2c)
        self.gain = adafruit_tsl2591.GAIN_MED
        self.integration_time = adafruit_tsl2591.INTEGRATIONTIME_300MS
        #self.integration_time = adafruit_tsl2591.INTEGRATIONTIME_500MS
        self.channel = 0

    @property
    def max_counts(self):
        if self.integration_time == adafruit_tsl2591.INTEGRATIONTIME_100MS:
            return self.TSL2591_MAX_COUNT_100MS 
        else:
            return self.TSL2591_MAX_COUNT 

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
