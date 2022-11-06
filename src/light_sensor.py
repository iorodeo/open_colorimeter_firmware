import busio
import board
import adafruit_tsl2591


class LightSensor:

    TSL2591_MAX_COUNT_100MS = 36863  # 0x8FFF
    TSL2591_MAX_COUNT = 65535        # 0xFFFF

    DEFAULT_GAIN = adafruit_tsl2591.GAIN_MED
    DEFAULT_INTEGRATION_TIME = adafruit_tsl2591.INTEGRATIONTIME_500MS

    def __init__(self):

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        try:
            self._device = adafruit_tsl2591.TSL2591(i2c)
        except ValueError as error:
            raise LightSensorIOError(error)
        self.gain = self.DEFAULT_GAIN 
        self.integration_time = self.DEFAULT_INTEGRATION_TIME 
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
        #print(value)
        return value

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

class LightSensorIOError(Exception):
    pass

