import os
import json
import constants
from collections import OrderedDict

class ConfigurationError(Exception):
    pass

class Configuration:

    FILE_TYPE = 'configuration'
    FILE_NAME = constants.CONFIGURATION_FILE
    LOAD_ERROR_EXCEPTION = ConfigurationError


    def __init__(self):
        super().__init__()

    def check(self):

        # Check gain
        try:
            gain = self.data['gain']
        except KeyError:
            error_msg = f'{self.FILE_TYPE} missing gain'
            error_dict['gain'] = error_msg
        else:
            try:
                setting = constants.GAIN_STR_TO_SETTING[gain]
            except KeyError:
                error_msg = f'{self.FILE_TYPE} unknown gain {gain}'
                error_dict['gain'] = error_msg

        # Check integration time
        try:
            itime = self.data['integration_time']
        except KeyError:
            error_msg = f'{self.FILE_TYPE} missing integration time'
            error_dict['integration_time'] = error_msg
        else:

            try:
                setting = constants.INTEGRATION_TIME_STR_TO_SETTING[itime]
            except KeyError:
                error_msg = f'{self.FILE_TYPE} unknown integration time {itime}'
                error_dict['integration_time'] = error_msg

        # Remove configurations with errors
        for name in self.error_dict:
            del self.data[name]
            
    
