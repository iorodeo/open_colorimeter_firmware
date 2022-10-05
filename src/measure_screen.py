import board
import displayio
import terminalio
import constants
import fonts
from adafruit_display_text import label


class MeasureScreen:

    SPACING_HEADER_LABEL = 7 
    SPACING_VALUE_LABEL = 12 
    SPACING_BLANK_LABEL = 8 

    INFO_XPOS = 10
    INFO_YPOS_START = board.DISPLAY.height - 36 
    INFO_YPOS_STEP = 14 

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
        header_str = 'Absorbance'
        text_color = constants.COLOR_TO_RGB['white']
        self.header_label = label.Label(
                fonts.hack_bold_14pt, 
                text = header_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5, 1.0),
                )
        bbox = self.header_label.bounding_box
        header_label_x = board.DISPLAY.width//2 
        header_label_y = bbox[3] + self.SPACING_HEADER_LABEL
        self.header_label.anchored_position = (header_label_x, header_label_y)

        # Create absorbance value text label
        dummy_value = 0.0
        value_str = f'{dummy_value:1.2f}'
        text_color = constants.COLOR_TO_RGB['white']
        self.value_label = label.Label(
                fonts.hack_bold_14pt, 
                text = value_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.value_label.bounding_box
        value_label_x = board.DISPLAY.width//2
        value_label_y = header_label_y + bbox[3] + self.SPACING_VALUE_LABEL
        self.value_label.anchored_position = (value_label_x, value_label_y)
        
        # Create text label for blanking info
        blank_str = 'initializing' 
        text_color = constants.COLOR_TO_RGB['orange']
        self.blank_label = label.Label(
                fonts.hack_bold_10pt, 
                text=blank_str, 
                color=text_color, 
                scale=font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.blank_label.bounding_box
        blank_label_x = board.DISPLAY.width//2 
        blank_label_y = value_label_y + bbox[3] + self.SPACING_BLANK_LABEL 
        self.blank_label.anchored_position = (blank_label_x, blank_label_y)

        # Create gain text label
        gain_str = 'gain med'
        text_color = constants.COLOR_TO_RGB['white']
        self.gain_label = label.Label(
                fonts.hack_bold_10pt, 
                text = gain_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.0,1.0),
                )
        bbox = self.gain_label.bounding_box
        gain_label_x = self.INFO_XPOS 
        gain_label_y = self.INFO_YPOS_START
        self.gain_label.anchored_position = (gain_label_x, gain_label_y)

        # Create integration time/window text label
        iwin_str = 'iwin 100ms'
        text_color = constants.COLOR_TO_RGB['white']
        self.iwin_label = label.Label(
                fonts.hack_bold_10pt, 
                text = iwin_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.0,1.0),
                )
        bbox = self.gain_label.bounding_box
        iwin_label_x = self.INFO_XPOS 
        iwin_label_y = gain_label_y + self.INFO_YPOS_STEP
        self.iwin_label.anchored_position = (iwin_label_x, iwin_label_y)

        # Create integration time/window text label
        vbat_str = 'vbat 0.0V'
        text_color = constants.COLOR_TO_RGB['white']
        self.vbat_label = label.Label(
                fonts.hack_bold_10pt, 
                text = vbat_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.0,1.0),
                )
        bbox = self.gain_label.bounding_box
        vbat_label_x = self.INFO_XPOS 
        vbat_label_y = iwin_label_y + self.INFO_YPOS_STEP
        self.vbat_label.anchored_position = (vbat_label_x, vbat_label_y)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.value_label)
        self.group.append(self.blank_label)
        self.group.append(self.gain_label)
        self.group.append(self.iwin_label)
        self.group.append(self.vbat_label)

    def set_measurement(self, name, units, value):
        if units is None:
            self.header_label.text = name
            self.value_label.text = f'{value:1.2f}'
        else:
            self.header_label.text = name
            self.value_label.text = f'{value:1.2f} {units}'

    def set_absorbance(self, absorbance):
        self.set_measurement('Absorbance', None, absorbance)

    def set_transmittance(self, transmittance):
        self.set_measurement('Transmittance', None, transmittance)

    def set_not_blanked(self):
        self.blank_label.text = ' not blanked'

    def set_blanking(self):
        self.blank_label.text = '  blanking  '

    def set_blanked(self):
        self.blank_label.text = '           '

    def set_vbat(self, value):
        self.vbat_label.text = f'bat {value:1.1f}V'

    def show(self):
        board.DISPLAY.show(self.group)

