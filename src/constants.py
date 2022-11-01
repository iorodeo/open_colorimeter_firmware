import board
import collections
import adafruit_tsl2591

LOOP_DT = 0.1
BLANK_DT = 0.05
DEBOUNCE_DT = 0.6 
NUM_BLANK_SAMPLES = 50 

BATTERY_AIN_PIN = board.A6
SPLASHSCREEN_BMP = 'assets/splashscreen.bmp'
CALIBRATIONS_FILE = 'calibrations.json'

BUTTON = { 
        'no button'   : 0b00000000,
        'menu_left'   : 0b10000000,
        'menu_up'     : 0b01000000,
        'menu_down'   : 0b00100000, 
        'menu_right'  : 0b00010000,
        'menu_toggle' : 0b00001000, 
        'blank'       : 0b00000100, 
        'time_cycle'  : 0b00000010,
        'gain_cycle'  : 0b00000001,
        }

COLOR_TO_RGB = collections.OrderedDict([ 
    ('black'  , 0x000000), 
    ('gray'   , 0x7f7f7f), 
    ('red'    , 0xff0000), 
    ('green'  , 0x00ff00),
    ('blue'   , 0x0000ff),
    ('white'  , 0xffffff), 
    ('orange' , 0xffb447),
    ])

GAIN_STR_TO_VALUE = collections.OrderedDict([
        ('low'  , adafruit_tsl2591.GAIN_LOW ),
        ('med'  , adafruit_tsl2591.GAIN_MED ),
        ('high' , adafruit_tsl2591.GAIN_HIGH),
        ('max'  , adafruit_tsl2591.GAIN_MAX ),
        ])

INTEGRATION_TIME_STR_TO_VALUE = collections.OrderedDict([
        ('100ms', adafruit_tsl2591.INTEGRATIONTIME_100MS),
        ('200ms', adafruit_tsl2591.INTEGRATIONTIME_200MS),
        ('300ms', adafruit_tsl2591.INTEGRATIONTIME_300MS),
        ('400ms', adafruit_tsl2591.INTEGRATIONTIME_400MS),
        ('500ms', adafruit_tsl2591.INTEGRATIONTIME_500MS),
        ('600ms', adafruit_tsl2591.INTEGRATIONTIME_600MS),
        ])
