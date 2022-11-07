import board
import displayio
import constants
import fonts
from adafruit_display_text import label
from adafruit_display_text import wrap_text_to_lines 


class MessageScreen:

    SPACING_HEADER_LABEL = 10 
    SPACING_MESSAGE_LABEL = 10  
    HEIGHT_MESSAGE_LABEL = 10
    MESSAGE_MAX_CHARS = 18
    NUM_MESSAGE_LABEL = 4

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

        # Create header label
        header_str = 'MESSAGE'
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

        # Create message labels
        self.message_label_list = []
        message_label_y = header_label_y + self.SPACING_MESSAGE_LABEL
        for i in range(self.NUM_MESSAGE_LABEL): 
            message_str = ' '*self.MESSAGE_MAX_CHARS
            text_color = constants.COLOR_TO_RGB['orange']
            message_label = label.Label(
                    fonts.font_10pt, 
                    text = message_str, 
                    color = text_color, 
                    scale = font_scale,
                    anchor_point = (0.5,1.0),
                    )
            bbox = message_label.bounding_box
            message_label_x = board.DISPLAY.width//2
            message_label_y += self.HEIGHT_MESSAGE_LABEL + self.SPACING_MESSAGE_LABEL 
            message_label.anchored_position = (message_label_x, message_label_y)
            self.message_label_list.append(message_label)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        for message_label in self.message_label_list:
            self.group.append(message_label)

    def set_message(self, message, ok_to_continue=True):
        if ok_to_continue:
            message_extended = f'{message}. Press any key to continue.'
        else:
            message_extended = f'{message}'
        wrapped_message = wrap_text_to_lines(message_extended, self.MESSAGE_MAX_CHARS) 
        for message_label, line in zip(self.message_label_list, wrapped_message):
            message_label.text = line  

    def set_header(self, header):
        self.header_label.text = header

    def set_to_error(self):
        self.header_label.text = 'Error'

    def set_to_abort(self):
        self.header_label.text = 'Abort'
        
    def set_to_about(self):
        self.header_label.text = 'About'

    def show(self):
        board.DISPLAY.show(self.group)

