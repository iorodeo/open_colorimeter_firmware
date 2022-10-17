import board
import displayio
import constants
import fonts
from adafruit_display_text import label


class ErrorScreen:

    SPACING_HEADER_LABEL = 18 
    SPACING_MESSAGE_LABEL =  16  

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
        header_str = 'Error'
        text_color = constants.COLOR_TO_RGB['white']
        self.header_label = label.Label(
                fonts.font_14pt, 
                text = header_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5, 1.0),
                )
        bbox = self.header_label.bounding_box
        header_label_x = board.DISPLAY.width//2 
        header_label_y = bbox[3] + self.SPACING_HEADER_LABEL
        self.header_label.anchored_position = (header_label_x, header_label_y)

        # Create error message text label
        error_message_str = 'some error'
        text_color = constants.COLOR_TO_RGB['orange']
        self.error_label = label.Label(
                fonts.font_10pt, 
                text = error_message_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.error_label.bounding_box
        error_label_x = board.DISPLAY.width//2
        error_label_y = header_label_y + bbox[3] + self.SPACING_MESSAGE_LABEL
        self.error_label.anchored_position = (error_label_x, error_label_y)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.error_label)

    def set_message(self, value):
        self.error_label.text = value

    def show(self):
        board.DISPLAY.show(self.group)

