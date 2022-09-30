import board
import displayio
import terminalio
import constants
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font


class MeasureScreen:

    def __init__(self):

        # Setup color palette
        self.color_to_index = {k:i for (i,k) in enumerate(constants.COLOR_TO_RGB)}
        self.palette = displayio.Palette(len(constants.COLOR_TO_RGB))
        for i, palette_tuple in enumerate(constants.COLOR_TO_RGB.items()):
            self.palette[i] = palette_tuple[1]   

        # Create tile grid
        self.bitmap = displayio.Bitmap( 
                board.DISPLAY.width, 
                board.DISPLAY.height, 
                len(constants.COLOR_TO_RGB)
                )
        self.bitmap.fill(self.color_to_index['black'])
        self.tile_grid = displayio.TileGrid(self.bitmap,pixel_shader=self.palette)
        self.font = terminalio.FONT

        # Create header text label
        header_str = 'ABSORBANCE'
        text_color = constants.COLOR_TO_RGB['white']
        self.header_label = label.Label(self.font, text=header_str, color=text_color, scale=2)
        bbox = self.header_label.bounding_box
        self.header_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.header_label.y = bbox[3] + 10 

        # Create absorbance value text label
        dummy_value = 0.0
        value_str = f'{dummy_value:1.2f}'
        text_color = constants.COLOR_TO_RGB['white']
        self.value_label = label.Label(self.font, text=value_str, color=text_color, scale=2)
        bbox = self.value_label.bounding_box
        self.value_label.x = board.DISPLAY.width//2 - 2*bbox[2]//2
        self.value_label.y = self.header_label.y + bbox[3] + 20 
        
        # Create text label for blanking info
        blank_str = 'INITIALIZING' 
        text_color = constants.COLOR_TO_RGB['white']
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
