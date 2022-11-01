import os
import ulab
import json
import constants
from collections import OrderedDict
from json_settings_file import JsonSettingsFile

class CalibrationsError(Exception):
    pass

class Calibrations(JsonSettingsFile):

    FILE_TYPE = 'calibrations'
    FILE_NAME = constants.CALIBRATIONS_FILE
    LOAD_ERROR_EXCEPTION = CalibrationsError
    ALLOWED_FIT_TYPES = ['linear', 'polynomial']

    def __init__(self):
        super().__init__()

    def check(self):
        # Check each calibration for errors
        for name, calibration in self.data.items():
            error_list = []
            error_list.extend(self.check_fit(name, calibration))
            error_list.extend(self.check_range(name, calibration))
            if error_list:
                self.error_dict[name] = error_list

        # Remove calibrations with errors
        for name in self.error_dict:
            del self.data[name]

    def check_fit(self,name, calibration): 
        error_list = []
        try:
            fit_type = calibration['fit_type']
        except KeyError:
            fit_type = None
            error_msg = f'{name} missing fit_type'
            error_list.append(error_msg)
        else:
            if not fit_type in self.ALLOWED_FIT_TYPES:
                error_msg = f'{name} unknown fit_type {fit_type}'
                error_list.append(error_msg)
        try:
            fit_coef = calibration['fit_coef']
        except KeyError:
            fit_coef = None
            error_msg = f'{name} missing fit_coef' 
            error_list.append(error_msg)
        else:
            try:
                fit_coef = ulab.numpy.array(fit_coef)
            except (ValueError, TypeError):
                error_msg = f'{name} fit coeff format incorrect'
                error_list.append(error_msg)
        if fit_type == 'linear' and fit_coef.size > 2:
            error_msg = f'{name} too many fit_coef for linear fit'
            error_list.append(error_msg)
        return error_list

    def check_range(self, name, calibration):
        min_value = None
        max_value = None
        error_list = []
        try:
            range_data = calibration['range']
        except KeyError:
            if fit_type != 'linear':
                error_msg = f'{name} range data missing'
                error_list.append(error_msg)
        else:
            if not type(range_data) == dict:
                error_msg = f'range_data must be dict'
                error_list.append(error_msg)
                return error_list

        try:
            min_value = float(range_data['min'])
        except KeyError:
            error_msg = f'{name} range min missing'
            error_list.append(error_msg)
        except (ValueError, TypeError): 
            error_msg = f'{name} range min not float' 
            error_list.append(error_msg)

        try:
            max_value = float(range_data['max'])
        except KeyError:
            error_msg = f'{name} range max missing'
            error_list.append(error_msg)
        except (ValueError, TypeError): 
            error_msg = f'{name} range max not float' 
            error_list.append(error_msg)

        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                error_msg = f'{name} range min > max'
                error_list.append(error_msg)

        return error_list

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
        fit_coef = ulab.numpy.array(self.data[name]['fit_coef'])
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


