import random
import collections
"""
dummy calibratin for development
"""


if 0:
    NUM_ITEM = 10
    UNITS_LIST = ['ppm', 'ppb', 'mg', 'uM']
    
    dummy_cal = collections.OrderedDict() 
    for i in range(NUM_ITEM): 
        dummy_cal[f'substance_{i+1}'] = { 
                'units'     : UNITS_LIST[random.randint(0,len(UNITS_LIST)-1)],
                'fit_type'  : 'linear' ,
                'fit_coef'  : [random.random(), 0.0], 
                'range'     : {'min': 0.0, 'max': 10*random.random()},
                'led'       : 630, 
                }

else:

    dummy_cal = {
            'FD&C Blue1' : {
                'units'    : 'mg', 
                'fit_type' : 'linear',
                'fit_coef' : [random.random(), 0.0], 
                'range'    : {'min': 0.0, 'max': 30.0}, 
                'led'      : 630, 
                }, 
            'Ammonnia' : {
                'units'    : 'ppm', 
                'fit_type' : 'linear',
                'fit_coef' : [random.random(), 0.0], 
                'range'    : {'min': 0.0, 'max': 8.0},
                'led'      : 630, 
                },
            'Nitrate' : {
                'units'     : 'ppm', 
                'fit_type'  : 'linear' ,
                'fit_coef'  : [random.random(), 0.0], 
                'range'     : {'min': 0.0, 'max': 200.0},
                'led'       : 520, 
                },
            'Phosphate' : {
                'units'     : 'ppm', 
                'fit_type'  : 'linear' ,
                'fit_coef'  : [random.random(), 0.0], 
                'range'     : {'min': 0.0, 'max': 30.0},
                'led'       : 630, 
                },
            'Sulfate' : {
                'units'     : 'ppm', 
                'fit_type'  : 'linear' ,
                'fit_coef'  : [random.random(), 0.0], 
                'range'     : {'min': 0.0, 'max': 300.0},
                'led'       : 520, 
                },
            'Calcium' : {
                'units'     : 'ppm', 
                'fit_type'  : 'linear' ,
                'fit_coef'  : [random.random(), 0.0], 
                'range'     : {'min': 0.0, 'max': 200.0},
                'led'       : 575, 
                },
            }


