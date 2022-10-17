import math
import analogio
import constants

class BatteryMonitor:

    VOLT_MAX = 4.2
    VOLT_MIN = 3.5
    VOLT_RNG = VOLT_MAX - VOLT_MIN
    VOLT_NUM_INIT = 20
    FREQ_CUTOFF = 0.02

    def __init__(self):
        self.battery_ain = analogio.AnalogIn(constants.BATTERY_AIN_PIN) 
        self.lowpass = None


    def update(self):
        if self.lowpass is None:
            self.lowpass = LowpassFilter(
                    freq_cutoff = self.FREQ_CUTOFF, 
                    value = self.raw_voltage,  
                    dt = constants.LOOP_DT
                    )
            for i in range(self.VOLT_NUM_INIT):
                self.lowpass.update(self.raw_voltage)
        else:
            self.lowpass.update(self.raw_voltage)

    @property
    def percent(self):
        return int(100*self.fraction)

    @property
    def fraction(self):
        return (self.lowpass.value - self.VOLT_MIN)/self.VOLT_RNG

    @property
    def voltage(self):
        if self.lowpass is None:
            return 0.0
        else:
            return self.lowpass.value

    @property
    def raw_voltage(self):
       return 2.0*ain_to_volt(self.battery_ain.value)


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
