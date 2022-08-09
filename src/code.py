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


class Colorimeter:

    NUM_BLANK = 50 
    BLANK_DT = 0.05
    BLANK_BUTTON = 2
    LOOP_DT = 0.1

    def __init__(self):

        # Set up color palette
        self.color_to_rgb = collections.OrderedDict({
                'black' : 0x000000, 
                'gray'  : 0x9f9f9f, 
                'red'   : 0xff0000, 
                'green' : 0x00ff00,
                'blue'  : 0x0000ff,
                'white' : 0xffffff,
                })
        self.color_to_index = {k:i for (i,k) in enumerate(self.color_to_rgb)}
        self.palette = displayio.Palette(len(self.color_to_rgb))
        for i, palette_tuple in enumerate(self.color_to_rgb.items()):
            self.palette[i] = palette_tuple[1]   

        # Create tile grid
        self.bitmap = displayio.Bitmap( 
                board.DISPLAY.width, 
                board.DISPLAY.height, 
                len(self.color_to_rgb)
                )
        self.bitmap.fill(self.color_to_index['black'])
        self.tile_grid = displayio.TileGrid(self.bitmap,pixel_shader=self.palette)
        self.font = terminalio.FONT

        # Create header text label
        header_str = 'ABSORBANCE'
        text_color = self.color_to_rgb['white']
        self.header_label = label.Label(self.font, text=header_str, color=text_color, scale=2)
        bbox = self.header_label.bounding_box
        self.header_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.header_label.y = bbox[3] + 10 

        # Create absorbance value text label
        dummy_value = 0.0
        value_str = f'{dummy_value:1.3f}'
        text_color = self.color_to_rgb['white']
        self.value_label = label.Label(self.font, text=value_str, color=text_color, scale=2)
        bbox = self.value_label.bounding_box
        self.value_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.value_label.y = self.header_label.y + bbox[3] + 20 
        
        # Create text label for blanking info
        blank_str = 'INITIALIZING' 
        text_color = self.color_to_rgb['red']
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
        board.DISPLAY.show(self.group)

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tsl2591.TSL2591(i2c)
        self.sensor.gain = adafruit_tsl2591.GAIN_HIGH

        # Get gamepad 
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Initialize sensor
        self.blank_value = 0.0
        self.blank_sensor()
        self.blank_label.text = 'NOT BLANKED'
        self.is_blanked = False
        board.DISPLAY.show(self.group)

    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((self.NUM_BLANK,))
        for i in range(self.NUM_BLANK):
            blank_samples[i] = float(self.sensor.full_spectrum)
            time.sleep(self.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)

    def run(self):
        while True:

            buttons = self.pad.get_pressed()
            if buttons & self.BLANK_BUTTON:
                self.blank_label.text = ' BLANKING  '
                self.blank_sensor()
                self.blank_label.text = '           '

            sensor_value = float(self.sensor.full_spectrum)
            transmittance = sensor_value/self.blank_value
            absorbance = -ulab.numpy.log10(transmittance)
            absorbance = absorbance if absorbance > 0.0 else 0.0
            self.value_label.text = f'{absorbance:1.3f}'

            time.sleep(self.LOOP_DT)
            board.DISPLAY.show(self.group)


# -------------------------------------------------------------------------------------------------------

colorimeter = Colorimeter()
colorimeter.run()


