import math
import analogio
import constants

class BatteryMonitor:

    def __init__(self):
        self.battery_ain = analogio.AnalogIn(constants.BATTERY_AIN_PIN) 
        self.lowpass = None

    def update(self):
        voltage = 2.0*ain_to_volt(self.battery_ain.value)
        if self.lowpass is None:
            self.lowpass = LowpassFilter(
                    freq_cutoff = 0.1, 
                    value = voltage, 
                    dt = constants.LOOP_DT
                    )
        else:
            self.lowpass.update(voltage)

    @property
    def voltage(self):
        if self.lowpass is None:
            return 0.0
        else:
            return self.lowpass.value


class LowpassFilter:

    def __init__(self, freq_cutoff=1.0, value=0.0, dt=1.0):
        self.dt = dt
        self.value = value
        self.freq_cutoff = freq_cutoff

    @property
    def freq_cutoff(self):
        return self._alpha/((1.0-self._alpha)*2.0*math.pi*self.dt)

    @freq_cutoff.setter
    def freq_cutoff(self, freq):
        self._alpha = (2.0*math.pi*self.dt*freq)/(2.0*math.pi*self.dt*freq+1)

    def update(self, new_value):
        self.value = self._alpha*new_value + (1.0-self._alpha)*self.value


def ain_to_volt(value):
    return 3.3*value/65536
