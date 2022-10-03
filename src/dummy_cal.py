import random
import collections
"""
dummy calibratin for development
"""

NUM_ITEM = 10
UNITS_LIST = ['ppm', 'ppb', 'mg', 'uM']

dummy_cal = collections.OrderedDict() 
for i in range(NUM_ITEM): 
    dummy_cal[f'substance_{i+1}'] = { 
            'units'     : UNITS_LIST[random.randint(0,len(UNITS_LIST)-1)],
            'fit_type'  : 'linear' ,
            'fit_coeff' : [random.random(), 0.0], 
            'range'     : {'min': 0.0, 'max': 10*random.random()},
            'led'       : 630, 
            }

