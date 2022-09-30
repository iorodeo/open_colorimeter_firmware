import time
import ulab
import busio
import board
import digitalio
import adafruit_tsl2591
import gamepadshift
import constants

from screens import SplashScreen, MeasureScreen

class Mode:
    SPLASH  = 0
    MEASURE = 1
    MENU    = 2


class Colorimeter:

    def __init__(self):
        # Create screens
        self.splash_screen = SplashScreen()
        self.measure_screen = MeasureScreen()
        self.mode = Mode.SPLASH 
        board.DISPLAY.show(self.splash_screen.group)

        # Setup gamepad inputs
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tsl2591.TSL2591(i2c)
        self.sensor.gain = adafruit_tsl2591.GAIN_MED
        self.channel = 0

        # Initialize sensor
        self.blank_value = 0.0
        self.blank_sensor()
        self.measure_screen.set_not_blanked()
        self.is_blanked = False

    def read_sensor(self):
        values = self.sensor.raw_luminosity
        return values[self.channel]


    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((constants.NUM_BLANK_SAMPLES,))
        for i in range(constants.NUM_BLANK_SAMPLES):
            sensor_value = self.read_sensor()
            blank_samples[i] = float(sensor_value)
            time.sleep(constants.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        print(bin(buttons))

        if buttons:
            button_dt = time.monotonic() - self.last_button_press
            if button_dt < constants.DEBOUNCE_DT:
                return
            self.last_button_press = time.monotonic()

            if self.mode == Mode.MEASURE:
                if buttons & constants.BLANK_BUTTON:
                    self.measure_screen.set_blanking()
                    self.blank_sensor()
                    self.measure_screen.set_blanked()
                if buttons & constants.MENU_TOGGLE_BUTTON:
                    self.mode = Mode.MENU
            elif self.mode == Mode.Menu:
                if buttons & constants.MENU_TOGGLE_BUTTON:
                    self.mode = Mode.MEASURE

    def run(self):
        while True:
            if self.mode == Mode.SPLASH:
                active_group = self.splash_screen.group
                if time.monotonic() > constants.SPLASH_DT:
                    self.mode = Mode.MEASURE
            elif self.mode == Mode.MEASURE:
                self.handle_button_press()
                sensor_value = float(self.read_sensor())
                transmittance = sensor_value/self.blank_value
                absorbance = -ulab.numpy.log10(transmittance)
                absorbance = absorbance if absorbance > 0.0 else 0.0
                self.measure_screen.set_absorbance(absorbance)
                active_group = self.measure_screen.group

            board.DISPLAY.show(active_group)
            time.sleep(constants.LOOP_DT)

# -----------------------------------------------------------------------------
def main():
    colorimeter = Colorimeter()
    colorimeter.run()

# -----------------------------------------------------------------------------
main()



