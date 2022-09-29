import time
import ulab
import busio
import board
import displayio
import digitalio
import terminalio
import adafruit_tsl2591
import collections
import gamepadshift
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

class Mode:
    SPLASH  = 0
    MEASURE = 1
    MENU    = 2

class Colorimeter:

    NUM_BLANK_SAMPLES = 50 
    BLANK_BUTTON = 0b100 
    MENU_TOGGLE_BUTTON = 0b1000

    LOOP_DT = 0.1
    BLANK_DT = 0.05
    SPLASH_DT = 4.0 
    DEBOUNCE_DT = 0.1 

    def __init__(self):

        self.mode = Mode.SPLASH 

        #self.setup_color_palette()
        self.splash_screen = SplashScreen()
        self.measure_screen = MeasureScreen()
        board.DISPLAY.show(self.splash_screen.group)

        # Setup gamepad inputs
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tsl2591.TSL2591(i2c)
        self.sensor.gain = adafruit_tsl2591.GAIN_MED
        self.channel = 0

        # Initialize sensor
        self.blank_value = 0.0
        self.blank_sensor()
        self.measure_screen.set_not_blanked()
        self.is_blanked = False

    def read_sensor(self):
        values = self.sensor.raw_luminosity
        return values[self.channel]


    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((self.NUM_BLANK_SAMPLES,))
        for i in range(self.NUM_BLANK_SAMPLES):
            sensor_value = self.read_sensor()
            blank_samples[i] = float(sensor_value)
            time.sleep(self.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        print(bin(buttons))

        if buttons:
            button_dt = time.monotonic() - self.last_button_press
            if button_dt < self.DEBOUNCE_DT:
                return
            self.last_button_press = time.monotonic()

            if self.mode == Mode.MEASURE:
                if buttons & self.BLANK_BUTTON:
                    self.measure_screen.set_blanking()
                    self.blank_sensor()
                    self.measure_screen.set_blanked()
                if buttons & self.MENU_TOGGLE_BUTTON:
                    self.mode = Mode.MENU
            elif self.mode == Mode.Menu:
                if buttons & self.MENU_TOGGLE_BUTTON:
                    self.mode = Mode.MEASURE

    def run(self):

        while True:

            if self.mode == Mode.SPLASH:
                active_group = self.splash_screen.group
                if time.monotonic() > self.SPLASH_DT:
                    self.mode = Mode.MEASURE
            elif self.mode == Mode.MEASURE:
                self.handle_button_press()
                sensor_value = float(self.read_sensor())
                transmittance = sensor_value/self.blank_value
                absorbance = -ulab.numpy.log10(transmittance)
                absorbance = absorbance if absorbance > 0.0 else 0.0
                self.measure_screen.set_absorbance(absorbance)
                active_group = self.measure_screen.group

            board.DISPLAY.show(active_group)
            time.sleep(self.LOOP_DT)


class MeasureScreen:

    COLOR_TO_RGB = collections.OrderedDict({ 
        'black' : 0x000000, 
        'gray'  : 0x9f9f9f, 
        'red'   : 0xff0000, 
        'green' : 0x00ff00,
        'blue'  : 0x0000ff,
        'white' : 0xffffff, 
        })

    def __init__(self):

        # Setup color palette
        self.color_to_index = {k:i for (i,k) in enumerate(self.COLOR_TO_RGB)}
        self.palette = displayio.Palette(len(self.COLOR_TO_RGB))
        for i, palette_tuple in enumerate(self.COLOR_TO_RGB.items()):
            self.palette[i] = palette_tuple[1]   

        # Create tile grid
        self.bitmap = displayio.Bitmap( 
                board.DISPLAY.width, 
                board.DISPLAY.height, 
                len(self.COLOR_TO_RGB)
                )
        self.bitmap.fill(self.color_to_index['black'])
        self.tile_grid = displayio.TileGrid(self.bitmap,pixel_shader=self.palette)
        self.font = terminalio.FONT

        # Create header text label
        header_str = 'ABSORBANCE'
        text_color = self.COLOR_TO_RGB['white']
        self.header_label = label.Label(self.font, text=header_str, color=text_color, scale=2)
        bbox = self.header_label.bounding_box
        self.header_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.header_label.y = bbox[3] + 10 

        # Create absorbance value text label
        dummy_value = 0.0
        value_str = f'{dummy_value:1.2f}'
        text_color = self.COLOR_TO_RGB['white']
        self.value_label = label.Label(self.font, text=value_str, color=text_color, scale=2)
        bbox = self.value_label.bounding_box
        self.value_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.value_label.y = self.header_label.y + bbox[3] + 20 
        
        # Create text label for blanking info
        blank_str = 'INITIALIZING' 
        text_color = self.COLOR_TO_RGB['white']
        self.blank_label = label.Label(self.font, text=blank_str, color=text_color, scale=1)
        bbox = self.blank_label.bounding_box
        self.blank_label.x = board.DISPLAY.width//2 - bbox[2]//2
        self.blank_label.y = self.value_label.y + bbox[3] + 20 
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.value_label)
        self.group.append(self.blank_label)

    def set_absorbance(self, absorbance):
        self.value_label.text = f'{absorbance:1.2f}'

    def set_not_blanked(self):
        self.blank_label.text = 'NOT BLANKED'

    def set_blanking(self):
        self.blank_label.text = ' BLANKING  '

    def set_blanked(self):
        self.blank_label.text = '           '



class SplashScreen:

    def __init__(self):
        self.bitmap = displayio.OnDiskBitmap('/assets/splashscreen_2.bmp')
        self.tile_grid = displayio.TileGrid(
                self.bitmap, 
                pixel_shader = self.bitmap.pixel_shader, 
                )
        self.group = displayio.Group()
        self.group.append(self.tile_grid)

# -------------------------------------------------------------------------------------------------------

colorimeter = Colorimeter()
colorimeter.run()


