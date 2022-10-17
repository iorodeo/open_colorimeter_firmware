import board
import displayio
import constants

class SplashScreen:

    def __init__(self):
        filename = f'{constants.SPLASHSCREEN_BMP}'
        self.bitmap = displayio.OnDiskBitmap(filename)
        self.tile_grid = displayio.TileGrid(
                self.bitmap, 
                pixel_shader = self.bitmap.pixel_shader, 
                )
        self.group = displayio.Group()
        self.group.append(self.tile_grid)

    def show(self):
        board.DISPLAY.show(self.group)
