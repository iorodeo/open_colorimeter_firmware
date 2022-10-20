import analogio
import constants
import ulab.numpy as np

class BatteryMonitor:

    VOLT_NUM_INIT = 5 
    FREQ_CUTOFF = 0.02

    def __init__(self):
        self.battery_ain = analogio.AnalogIn(constants.BATTERY_AIN_PIN) 
        self.lowpass = None

    def update(self):
        # Initialize lowpass filter
        if self.lowpass is None:
            # First reading or so is low for some reason. Throw a couple away 
            # rather than initialize lowpass filter to low value.
            for i in range(self.VOLT_NUM_INIT):
                dummy = self.voltage_raw
            self.lowpass = LowpassFilter(
                    freq_cutoff = self.FREQ_CUTOFF, 
                    value = self.voltage_raw,  
                    dt = constants.LOOP_DT
                    )
        else:
            # Update filter on new reading
            self.lowpass.update(self.voltage_raw)

    @property
    def voltage_lowpass(self):
        if self.lowpass is None:
            return 0.0
        else:
            return self.lowpass.value

    @property
    def voltage_raw(self):
       return 2.0*ain_to_volt(self.battery_ain.value)


class LowpassFilter:

    def __init__(self, freq_cutoff=1.0, value=0.0, dt=1.0):
        self.dt = dt
        self.value = value
        self.freq_cutoff = freq_cutoff

    @property
    def freq_cutoff(self):
        return self._alpha/((1.0-self._alpha)*2.0*np.pi*self.dt)

    @freq_cutoff.setter
    def freq_cutoff(self, freq):
        self._alpha = (2.0*np.pi*self.dt*freq)/(2.0*np.pi*self.dt*freq+1)

    def update(self, new_value):
        self.value = self._alpha*new_value + (1.0-self._alpha)*self.value


def ain_to_volt(value):
    return 3.3*value/65536
