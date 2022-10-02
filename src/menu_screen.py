import board
import displayio
import terminalio
import constants
import fonts
from adafruit_display_text import label

class MenuScreen:

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
        font_scale = 1

        # Create header text label
        header_str = 'Menu'
        text_color = constants.COLOR_TO_RGB['white']
        self.header_label = label.Label(
                fonts.hack_bold_14pt, 
                text=header_str, 
                color=text_color, 
                scale=font_scale
                )
        bbox = self.header_label.bounding_box
        self.header_label.x = board.DISPLAY.width//2 - font_scale*bbox[2]//2
        self.header_label.y = bbox[3]  

        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
