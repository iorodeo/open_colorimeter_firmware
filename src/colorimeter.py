import os
import time
import ulab
import json
import board
import analogio
import digitalio
import gamepadshift
import constants
import dummy_cal

from light_sensor import LightSensor
from light_sensor import LightSensorOverflow
from battery_monitor import BatteryMonitor

from menu_screen import MenuScreen
from error_screen import ErrorScreen
from measure_screen import MeasureScreen

class Mode:
    MEASURE = 0
    MENU    = 1

class Colorimeter:

    def __init__(self):

        self.battery_monitor = BatteryMonitor()

        # Create screens
        board.DISPLAY.brightness = 1.0
        self.measure_screen = MeasureScreen()
        self.error_screen = ErrorScreen()
        self.menu_screen = MenuScreen()

        # Setup gamepad inputs - change this (Keypad shift??)
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Load calibrations and populae menu items
        self.load_calibrations()
        self.menu_items = ['Absorbance', 'Transmittance']
        self.menu_items.extend([k for k in self.calibrations])
        self.mode = Mode.MEASURE
        self.menu_view_pos = 0
        self.menu_item_pos = 0
        self.measurement = self.menu_items[0] 

        # Setup light sensor and blanking data 
        self.light_sensor = LightSensor()
        self.blank_value = 0.0
        self.blank_sensor()
        self.measure_screen.set_not_blanked()
        self.is_blanked = False


    def load_calibrations(self):
        self.calibrations = {}
        if constants.CALIBRATIONS_FILE in os.listdir():
            try:
                with open(constants.CALIBRATIONS_FILE,'r') as f:
                    self.calibrations = json.load(f)
            except (OSError, ValueError) as error:
                # TODO: need to create some sort of temporary error screen 
                # for when we can't parse file
                pass

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

    @property
    def transmittance(self):
        transmittance = self.light_sensor.value/self.blank_value
        return transmittance

    @property
    def absorbance(self):
        absorbance = -ulab.numpy.log10(self.transmittance)
        absorbance = absorbance if absorbance > 0.0 else 0.0
        return absorbance

    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((constants.NUM_BLANK_SAMPLES,))
        for i in range(constants.NUM_BLANK_SAMPLES):
            try:
                value = self.light_sensor.value
            except LightSensorOverflow:
                value = self.light_sensor.max_counts
            blank_samples[i] = value 
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
                    try:
                        self.measure_screen.set_absorbance(self.absorbance)
                    except LightSensorOverflow:
                        self.measure_screen.set_absorbance_overflow()
                elif self.measurement == 'Transmittance':
                    try:
                        self.measure_screen.set_transmittance(self.transmittance)
                    except LightSensorOverflow:
                        self.measure_screen.set_transmittance_overflow()
                else:
                    name = self.measurement
                    units = self.calibrations[self.measurement]['units']
                    value = 0.0
                    self.measure_screen.set_measurement(name, units, value)

                self.battery_monitor.update()
                self.measure_screen.set_bat(self.battery_monitor.voltage_lowpass)
                #self.measure_screen.set_bat(self.battery_monitor.percent)
                #print(f'{self.battery_monitor.voltage_raw} {self.battery_monitor.voltage_lowpass} {self.battery_monitor.fraction}')
                self.measure_screen.show()

            elif self.mode == Mode.MENU:
                self.menu_screen.show()

            time.sleep(constants.LOOP_DT)

