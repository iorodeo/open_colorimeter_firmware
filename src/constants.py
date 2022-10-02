import collections

LOOP_DT = 0.1
BLANK_DT = 0.05
DEBOUNCE_DT = 0.3 

NUM_BLANK_SAMPLES = 50 

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

COLOR_TO_RGB = collections.OrderedDict({ 
    'black'  : 0x000000, 
    'gray'   : 0x9f9f9f, 
    'red'    : 0xff0000, 
    'green'  : 0x00ff00,
    'blue'   : 0x0000ff,
    'white'  : 0xffffff, 
    'orange' : 0xffb447
    })

SPLASHSCREEN_BMP = 'splashscreen.bmp'
