import board
import displayio
import constants
import fonts
from adafruit_display_text import label


class MeasureScreen:

    HEADER_LABEL_Y_SPACING = 18 
    VALUE_LABEL_Y_SPACING =  16  
    BLANK_LABEL_Y_SPACING = 14  
    GAIN_LABEL_X_SPACING = 3      
    ITIME_LABEL_X_SPACING = 15      
    GAIN_ITIME_LABELS_Y_SPACING = 14  
    BATTERY_LABEL_Y_SPACING = 16
    BATTERY_LABEL_X_POSITION = 10      

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
        header_label_y = bbox[3] + self.HEADER_LABEL_Y_SPACING
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
        value_label_y = header_label_y + bbox[3] + self.VALUE_LABEL_Y_SPACING
        self.value_label.anchored_position = (value_label_x, value_label_y)
        
        # Create text label for blanking info
        # Note: not shown when gain and time labels are shown
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
        blank_label_y = value_label_y + bbox[3] + self.BLANK_LABEL_Y_SPACING 
        self.blank_label.anchored_position = (blank_label_x, blank_label_y)

        # Create text label for gain information
        # Note: not shown when blanking label is shown
        gain_str = 'gain xxx' 
        text_color = constants.COLOR_TO_RGB['orange']
        self.gain_label = label.Label(
                fonts.font_10pt, 
                text=gain_str, 
                color=text_color, 
                scale=font_scale,
                anchor_point = (0.0,1.0),
                )
        gain_bbox = self.gain_label.bounding_box
        gain_label_x  = self.GAIN_LABEL_X_SPACING
        gain_label_y  = value_label_y + gain_bbox[3] 
        gain_label_y += self.GAIN_ITIME_LABELS_Y_SPACING 
        self.gain_label.anchored_position = (gain_label_x, gain_label_y)

        # Create text label for integration time information
        # Note: not shown when blanking label is shown
        itime_str = 'time xxxms' 
        text_color = constants.COLOR_TO_RGB['orange']
        self.itime_label = label.Label(
                fonts.font_10pt, 
                text=itime_str, 
                color=text_color, 
                scale=font_scale,
                anchor_point = (0.0,1.0),
                )
        itime_bbox = self.itime_label.bounding_box
        itime_label_x  = gain_label_x + gain_bbox[2] 
        itime_label_x += self.ITIME_LABEL_X_SPACING
        itime_label_y  = value_label_y + itime_bbox[3] 
        itime_label_y += self.GAIN_ITIME_LABELS_Y_SPACING 
        self.itime_label.anchored_position = (itime_label_x, itime_label_y)

        # Create integration time/window text label
        #bat_str = 'battery 100%'
        bat_str = 'battery 0.0V'
        text_color = constants.COLOR_TO_RGB['gray']
        self.bat_label = label.Label(
                fonts.font_10pt, 
                text = bat_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5,1.0),
                )
        bbox = self.bat_label.bounding_box
        bat_label_x = board.DISPLAY.width//2 
        bat_label_y = blank_label_y + bbox[3] + self.BATTERY_LABEL_Y_SPACING 
        self.bat_label.anchored_position = (bat_label_x, bat_label_y)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        self.group.append(self.value_label)
        self.group.append(self.blank_label)
        self.group.append(self.gain_label)
        self.group.append(self.itime_label)
        self.group.append(self.bat_label)

    def set_measurement(self, name, units, value, precision):
        if value is None:
            self.value_label.color = constants.COLOR_TO_RGB['orange']
            self.value_label.text = 'range error' 
        else:
            if units is None:
                self.header_label.text = name
                if type(value) == float:
                    label_text = f'{value:1.{precision}f}'
                else: 
                    label_text = f'{value}'
            else:
                self.header_label.text = name
                label_text = f'{value:1.{precision}f} {units}'
            self.value_label.text = label_text.replace('0','O')
            self.value_label.color = constants.COLOR_TO_RGB['white']

    def set_overflow(self, name):
        self.header_label.text = name
        self.value_label.text = 'overflow' 
        self.value_label.color = constants.COLOR_TO_RGB['red']

    def set_not_blanked(self):
        self.blank_label.text = ' not blanked'

    def set_blanking(self):
        self.blank_label.text = '  blanking  '

    def set_blanked(self):
        self.blank_label.text = ''

    def set_gain(self,value):
        if value is not None:
            value_str = constants.GAIN_TO_STR[value]
            self.gain_label.text = f'gain={value_str}'
        else:
            self.gain_label.text = ''

    def clear_gain(self):
        self.set_gain(None)

    def set_integration_time(self,value):
        if value is not None:
            value_str = constants.INTEGRATION_TIME_TO_STR[value]
            self.itime_label.text = f'time={value_str}'
        else:
            self.itime_label.text = ''

    def clear_integration_time(self):
        self.set_integration_time(None)

    def set_bat(self, value):
        self.bat_label.text = f'battery {value:1.1f}V'

    def show(self):
        board.DISPLAY.show(self.group)

