import board
import displayio
import constants
import fonts
from adafruit_display_text import label
from adafruit_display_text import wrap_text_to_lines 


class ErrorScreen:

    SPACING_HEADER_LABEL = 10 
    SPACING_MESSAGE_LABEL = 10  
    HEIGHT_MESSAGE_LABEL = 10
    MESSAGE_MAX_CHARS = 18
    NUM_ERROR_LABEL = 4

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
        header_str = 'ERROR'
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

        # Create error message labels
        self.error_label_list = []
        error_label_y = header_label_y + self.SPACING_MESSAGE_LABEL
        print(error_label_y)
        for i in range(self.NUM_ERROR_LABEL): 
            error_message_str = ' '*self.MESSAGE_MAX_CHARS
            text_color = constants.COLOR_TO_RGB['orange']
            error_label = label.Label(
                    fonts.font_10pt, 
                    text = error_message_str, 
                    color = text_color, 
                    scale = font_scale,
                    anchor_point = (0.5,1.0),
                    )
            bbox = error_label.bounding_box
            error_label_x = board.DISPLAY.width//2
            error_label_y += self.HEIGHT_MESSAGE_LABEL + self.SPACING_MESSAGE_LABEL 
            print(error_label_y)
            error_label.anchored_position = (error_label_x, error_label_y)
            self.error_label_list.append(error_label)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        for error_label in self.error_label_list:
            self.group.append(error_label)

    def set_message(self, message):
        message_extended = f'{message} Press any key to continue.'
        wrapped_message = wrap_text_to_lines(message_extended, self.MESSAGE_MAX_CHARS) 
        for item in wrapped_message:
            print(f'{len(item)}, {item}')
        for error_label, line in zip(self.error_label_list, wrapped_message):
            error_label.text = line  

    def show(self):
        board.DISPLAY.show(self.group)

