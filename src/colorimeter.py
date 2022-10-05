import time
import ulab
import busio
import board
import analogio
import digitalio
import adafruit_tsl2591
import gamepadshift
import constants

import dummy_cal
from battery_monitor import BatteryMonitor
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
        board.DISPLAY.brightness = 1.0

        # Setup gamepad inputs - change this (Keypad shift??)
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Load dummy calibrations for developement
        self.calibrations = dummy_cal.dummy_cal
        self.menu_items = ['Absorbance', 'Transmittance']
        self.menu_items.extend([k for k in self.calibrations])

        # Set up light sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tsl2591.TSL2591(i2c)
        self.sensor.gain = adafruit_tsl2591.GAIN_MED
        self.sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
        self.channel = 0


        # Initialize state 
        self.battery_monitor = BatteryMonitor()
        self.blank_value = 0.0
        self.blank_sensor()
        self.measure_screen.set_not_blanked()
        self.is_blanked = False
        self.mode = Mode.MEASURE
        self.menu_view_pos = 0
        self.menu_item_pos = 0
        self.measurement = self.menu_items[0] 

    @property
    def num_menu_items(self):
        return len(self.menu_items)

    def incr_menu_item_pos(self):
        if self.menu_item_pos < self.num_menu_items-1:
            self.menu_item_pos += 1
        diff_pos = self.menu_item_pos - self.menu_view_pos
        if diff_pos > self.menu_screen.items_per_screen-1:
            self.menu_view_pos += 1

    def decr_menu_item_pos(self):
        if self.menu_item_pos > 0:
            self.menu_item_pos -= 1
        if self.menu_item_pos < self.menu_view_pos:
            self.menu_view_pos -= 1

    def update_menu_screen(self):
        n0 = self.menu_view_pos
        n1 = n0 + self.menu_screen.items_per_screen
        view_items = []
        for i, item in enumerate(self.menu_items[n0:n1]):
            try:
                led = self.calibrations[item]['led']
                item_text = f'{n0+i} {item} ({led})' 
            except KeyError:
                item_text = f'{n0+i} {item}' 
            view_items.append(item_text)
        self.menu_screen.set_menu_items(view_items)
        pos = self.menu_item_pos - self.menu_view_pos
        self.menu_screen.set_curr_item(pos)

    def read_sensor(self):
        return float(self.sensor.raw_luminosity[self.channel])

    def get_transmittance(self):
        sensor_value = self.read_sensor()
        transmittance = sensor_value/self.blank_value
        return transmittance

    def get_absorbance(self):
        transmittance = self.get_transmittance()
        absorbance = -ulab.numpy.log10(transmittance)
        absorbance = absorbance if absorbance > 0.0 else 0.0
        return absorbance

    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((constants.NUM_BLANK_SAMPLES,))
        for i in range(constants.NUM_BLANK_SAMPLES):
            blank_samples[i] = self.read_sensor()
            time.sleep(constants.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        if buttons:
            if not self.check_debounce():
                return 
            else:
                self.last_button_press = time.monotonic()

            if self.mode == Mode.MEASURE:
                if buttons & constants.BUTTON['blank']:
                    self.measure_screen.set_blanking()
                    self.blank_sensor()
                    self.measure_screen.set_blanked()
                elif buttons & constants.BUTTON['menu_toggle']:
                    self.mode = Mode.MENU
                    self.menu_item_pos = 0
                    self.update_menu_screen()

            elif self.mode == Mode.MENU:
                if buttons & constants.BUTTON['menu_toggle']:
                    self.mode = Mode.MEASURE
                elif buttons & constants.BUTTON['menu_up']:
                    self.decr_menu_item_pos()
                elif buttons & constants.BUTTON['menu_down']:
                    self.incr_menu_item_pos()
                elif buttons & constants.BUTTON['menu_right']:
                    self.measurement = self.menu_items[self.menu_item_pos]
                    self.mode = Mode.MEASURE
                self.update_menu_screen()

    def check_debounce(self):
        button_dt = time.monotonic() - self.last_button_press
        if button_dt < constants.DEBOUNCE_DT: 
            return False
        else:
            return True

    def print_button_info(self, buttons):
        buttons_to_name = {v:k for k,v in constants.BUTTON.items()}
        print(buttons_to_name[buttons], self.mode)

    def run(self):
        while True:
            self.handle_button_press()
            if self.mode == Mode.MEASURE:
                if self.measurement == 'Absorbance':
                    absorbance = self.get_absorbance()
                    self.measure_screen.set_absorbance(absorbance)
                elif self.measurement == 'Transmittance':
                    transmittance = self.get_transmittance()
                    self.measure_screen.set_transmittance(transmittance)
                else:
                    name = self.measurement
                    units = self.calibrations[self.measurement]['units']
                    value = 0.0
                    self.measure_screen.set_measurement(name, units, value)
                self.battery_monitor.update()
                self.measure_screen.set_vbat(self.battery_monitor.voltage)
                self.measure_screen.show()
            elif self.mode == Mode.MENU:
                self.menu_screen.show()
            time.sleep(constants.LOOP_DT)


