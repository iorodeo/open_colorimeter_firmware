import board
import displayio
import terminalio
import constants
import fonts
from adafruit_display_text import label
from adafruit_display_shapes import line 

class MenuScreen:

    PADDING_HEADER = 4
    PADDING_ITEM = 5

    def __init__(self):
        self.group = displayio.Group()

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
        self.header_label = label.Label(
                fonts.font_14pt, 
                text = header_str, 
                color = constants.COLOR_TO_RGB['white'], 
                scale = font_scale,
                anchor_point = (0.5, 1.0)
                )
        header_x = board.DISPLAY.width//2 
        header_y = self.header_label.bounding_box[3] + self.PADDING_HEADER 
        self.header_label.anchored_position = header_x, header_y

        # Create line under menu
        menu_line_x0 = 0
        menu_line_y0 = header_y + self.PADDING_HEADER 
        menu_line_x1 = board.DISPLAY.width
        menu_line_y1 = menu_line_y0
        self.menu_line = line.Line(
                menu_line_x0, 
                menu_line_y0, 
                menu_line_x1, 
                menu_line_y1, 
                constants.COLOR_TO_RGB['gray']
                )

        # Test populate some items
        vert_pix_remaining = board.DISPLAY.height - (menu_line_y1 + 1)
        test_label = label.Label(fonts.font_10pt, text='test',scale=font_scale)
        label_dy = test_label.bounding_box[3] + self.PADDING_ITEM
        self.items_per_screen = vert_pix_remaining//label_dy

        self.item_labels = []
        for i in range(self.items_per_screen): 
            pos_x = 2
            pos_y = menu_line_y0 + (i+1)*label_dy 
            label_tmp = label.Label(
                     fonts.font_10pt,
                     text = '',
                     color = constants.COLOR_TO_RGB['white'],
                     scale = font_scale,
                     anchor_point = (0.0, 1.0),
                     anchored_position = (pos_x, pos_y),
                     padding_right = 160
                     )
            self.item_labels.append(label_tmp)

        # Ceate display group and add items to it
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.menu_line)
        for item_label in self.item_labels:
            self.group.append(item_label)

        self.set_curr_item(0)

    def set_menu_items(self, text_list):
        for item_label, item_text in zip(self.item_labels, text_list):
            item_label.text = item_text 

    def set_curr_item(self, num):
        for i, item_label in enumerate(self.item_labels):
            if i==num:
                item_label.color = constants.COLOR_TO_RGB['black']
                item_label.background_color = constants.COLOR_TO_RGB['orange']
            else:
                item_label.color = constants.COLOR_TO_RGB['white']
                item_label.background_color = constants.COLOR_TO_RGB['black']

    def show(self):
        board.DISPLAY.show(self.group)
