import os
import json
import constants
from collections import OrderedDict
from json_settings_file import JsonSettingsFile

class ConfigurationError(Exception):
    pass

class Configuration(JsonSettingsFile):

    FILE_TYPE = 'configuration'
    FILE_NAME = constants.CONFIGURATION_FILE
    LOAD_ERROR_EXCEPTION = ConfigurationError
    ALLOWED_PRECISION = (2,3,4)
    DEFAULT_PRECISION = 2

    def __init__(self):
        super().__init__()

    def check(self):

        # Check gain
        try:
            gain_str = self.data['gain']
        except KeyError:
            error_msg = f'{self.FILE_TYPE} missing gain'
            error_dict['gain'] = error_msg
        else:
            try:
                gain = constants.STR_TO_GAIN[gain_str]
            except KeyError:
                error_msg = f'{self.FILE_TYPE} unknown gain {gain_str}'
                error_dict['gain'] = error_msg

        # Check integration time
        try:
            itime_str = self.data['integration_time']
        except KeyError:
            error_msg = f'{self.FILE_TYPE} missing integration time'
            error_dict['integration_time'] = error_msg
        else:

            try:
                itime = constants.STR_TO_INTEGRATION_TIME[itime_str]
            except KeyError:
                error_msg = f'{self.FILE_TYPE} unknown integration time {itime_str}'
                error_dict['integration_time'] = error_msg

        # Remove configurations with errors
        for name in self.error_dict:
            del self.data[name]

        # Check precision
        self.data.setdefault('precision', self.DEFAULT_PRECISION)
        try:
            precision = self.data['precision']
        except KeyError:
            pass
        else:
            if not precision in self.ALLOWED_PRECISION:
                error_msg = f'precision must be in{self.ALLOWED_PRECISION}'
                error_dict['precision'] = error_msg

    @property
    def integration_time(self):
        try:
            itime_str = self.data['integration_time']
        except KeyError:
            itime = None
        else:
            itime = constants.STR_TO_INTEGRATION_TIME[itime_str]
        return itime

    @property
    def gain(self):
        try:
            gain_str = self.data['gain']
        except KeyError:
            gain = None
        else:
            gain = constants.STR_TO_GAIN[gain_str]
        return gain

    @property
    def startup(self):
        return self.data.get('startup', None)

    @property
    def precision(self):
        return self.data['precision']



            
            
    
