import os
import ulab
import json
import constants
from collections import OrderedDict

class Calibrations:

    def __init__(self):
        self.data = {}

    def load(self):
        self.data = {}
        if constants.CALIBRATIONS_FILE in os.listdir():
            try:
                with open(constants.CALIBRATIONS_FILE,'r') as f:
                    data = json.load(f)
            except (OSError, ValueError) as error:
                error_message = 'Unable to read data.json.'
                self.error_screen.set_message(error_message)
                self.mode = Mode.ERROR
            else:
                data_tuples = [(k,v) for (k,v) in data.items()]
                data_tuples.sort()
                self.data = OrderedDict(data_tuples) 
                self.check()

    def check(self):
        for k, v in self.data.items():
            pass

    def led(self, name):
        try:
            led = self.data[name]['led']
        except KeyError:
            led = None
        return led

    def units(self, name):
        try:
            units = self.data[name]['units']
        except KeyError:
            units = None
        return units

    def apply(self, name, absorbance):
        fit_type = self.data[name]['fit_type']
        fit_coef = self.data[name]['fit_coef']
        if fit_type in ('linear', 'polynomial'):
            try:
                range_min = self.data[name]['range']['min']
                range_max = self.data[name]['range']['max']
            except KeyError:
                pass
            else:
                if absorbance >= range_min and absorbance <= range_max:
                    value = ulab.numpy.polyval(fit_coef, [absorbance])[0]
                else:
                    value = None # out of range
        else:
            error_message = f'{fit_type} fit type not implemented'
            self.error_screen.set_message(error_message)
            self.measurement_name = 'Absorbance'
            self.mode = Mode.ERROR
            value = 0.0
        return value



