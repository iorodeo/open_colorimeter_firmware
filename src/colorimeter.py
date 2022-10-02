import time
import ulab
import busio
import board
import digitalio
import adafruit_tsl2591
import gamepadshift
import constants

from measure_screen import MeasureScreen
from menu_screen import MenuScreen

class Mode:
    MEASURE = 0
    MENU    = 1

class Colorimeter:

    def __init__(self):
        # Create screens
        self.measure_screen = MeasureScreen()
        self.menu_screen = MenuScreen()
        self.mode = Mode.MEASURE
        board.DISPLAY.brightness = 1.0

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

        if buttons:
            if not self.check_debounce():
                return 
            else:
                self.last_button_press = time.monotonic()
            self.print_button_info(buttons)

            if self.mode == Mode.MEASURE:
                if buttons & constants.BUTTON['blank']:
                    self.measure_screen.set_blanking()
                    self.blank_sensor()
                    self.measure_screen.set_blanked()
                if buttons & constants.BUTTON['menu_toggle']:
                    self.mode = Mode.MENU
            elif self.mode == Mode.MENU:
                if buttons & constants.BUTTON['menu_toggle']:
                    self.mode = Mode.MEASURE

    def check_debounce(self):
        button_dt = time.monotonic() - self.last_button_press
        if button_dt < constants.DEBOUNCE_DT: 
            return False
        else:
            return True

    def print_button_info(self, buttons):
        buttons_to_name = {v:k for k,v in constants.BUTTON.items()}
        #print(buttons, bin(buttons))
        print(buttons_to_name[buttons], self.mode)


    def run(self):
        while True:
            self.handle_button_press()
            if self.mode == Mode.MEASURE:
                sensor_value = float(self.read_sensor())
                transmittance = sensor_value/self.blank_value
                absorbance = -ulab.numpy.log10(transmittance)
                absorbance = absorbance if absorbance > 0.0 else 0.0
                self.measure_screen.set_absorbance(absorbance)
                active_group = self.measure_screen.group
            elif self.mode == Mode.MENU:
                active_group = self.menu_screen.group
            board.DISPLAY.show(active_group)
            time.sleep(constants.LOOP_DT)
