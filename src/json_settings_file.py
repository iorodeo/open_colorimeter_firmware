import os
import json
import constants
from collections import OrderedDict

class JsonSettingsError(Exception):
    pass

class JsonSettingsFile:

    FILE_TYPE = 'json settings'
    FILE_NAME = 'json_settings.json'
    LOAD_ERROR_EXCEPTION = JsonSettingsError 

    def __init__(self):
        self.data = {}
        self.error_dict = OrderedDict()

    @property
    def has_errors(self):
        return bool(self.error_dict)
    
    def pop_error(self):
        if self.error_dict:
            name = next(iter(self.error_dict))
            if type(self.error_dict[name]) == list:
                error_msg = self.error_dict[name].pop()
                if not self.error_dict[name]:
                    del self.error_dict[name]
            else:
                error_msg = self.error_dict[name]
                del self.error_dict[name]
        else:
            error_msg = None
        return error_msg

    def load(self):
        self.data = {}
        if self.FILE_NAME in os.listdir():
            try:
                with open(self.FILE_NAME, 'r') as f:
                    data = json.load(f)
            except (OSError, ValueError):
                error_msg = f'unable to read {self.FILE_TYPE} file'
                raise self.LOAD_ERROR_EXCEPTION(error_msg)
            else:
                if type(data) != dict:
                    error_msg = f'{self.FILE_TYPE} file incorrect format'
                    raise self.LOAD_ERROR_EXCEPTION(error_msg)
                data_tuples = [(k,v) for (k,v) in data.items()]
                data_tuples.sort()
                self.data = OrderedDict(data_tuples) 
                self.check()

    def check(self):
        pass


