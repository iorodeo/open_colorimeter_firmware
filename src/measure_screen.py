import board
import displayio
import terminalio
import constants
import fonts
from adafruit_display_text import label


class MeasureScreen:

    SPACING_HEADER_LABEL = 18 
    SPACING_VALUE_LABEL =  16  
    SPACING_BLANK_LABEL = 14  

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

        # Create absorbance value text label
        dummy_value = 0.0
        value_str = f'{dummy_value:1.2f}'.replace('0','O')
        text_color = constants.COLOR_TO_RGB['white']
        self.value_label = label.Label(
                fonts.font_14pt, 
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
                fonts.font_10pt, 
                text=blank_str, 
                color=text_color, 
                scale=font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.blank_label.bounding_box
        blank_label_x = board.DISPLAY.width//2 
        blank_label_y = value_label_y + bbox[3] + self.SPACING_BLANK_LABEL 
        self.blank_label.anchored_position = (blank_label_x, blank_label_y)

        # Create integration time/window text label
        vbat_str = 'battery 100%'
        text_color = constants.COLOR_TO_RGB['gray']
        self.vbat_label = label.Label(
                fonts.font_10pt, 
                text = vbat_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.vbat_label.bounding_box
        vbat_label_x = board.DISPLAY.width//2 
        vbat_label_y = 120 
        self.vbat_label.anchored_position = (vbat_label_x, vbat_label_y)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.value_label)
        self.group.append(self.blank_label)
        self.group.append(self.vbat_label)

    def set_measurement(self, name, units, value):
        if units is None:
            self.header_label.text = name
            label_text = f'{value:1.2f}'
        else:
            self.header_label.text = name
            label_text = f'{value:1.2f} {units}'
        self.value_label.text = label_text.replace('0','O')
        self.value_label.color = constants.COLOR_TO_RGB['white']

    def set_absorbance(self, absorbance):
        self.set_measurement('Absorbance', None, absorbance)

    def set_transmittance(self, transmittance):
        self.set_measurement('Transmittance', None, transmittance)

    def set_measurement_overflow(self, name):
        self.header_label.text = name
        self.value_label.text = 'overflow' 
        self.value_label.color = constants.COLOR_TO_RGB['red']

    def set_absorbance_overflow(self):
        self.set_measurement_overflow('Absorbance')

    def set_transmittance_overflow(self):
        self.set_measurement_overflow('Transmittance')

    def set_not_blanked(self):
        self.blank_label.text = ' not blanked'

    def set_blanking(self):
        self.blank_label.text = '  blanking  '

    def set_blanked(self):
        self.blank_label.text = '           '

    def set_bat(self, value):
        percent_str = f'{value}%'
        percent_pad = ' '*(4 - len(percent_str))
        battery_str = f'battery {percent_pad}{percent_str}'
        self.vbat_label.text = battery_str 

    def show(self):
        board.DISPLAY.show(self.group)

