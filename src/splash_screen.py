import displayio
import constants

class SplashScreen:

    def __init__(self):
        filename = f'/assets/{constants.SPLASHSCREEN_BMP}'
        self.bitmap = displayio.OnDiskBitmap(filename)
        self.tile_grid = displayio.TileGrid(
                self.bitmap, 
                pixel_shader = self.bitmap.pixel_shader, 
                )
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
