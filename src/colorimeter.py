import time
import ulab
import board
import analogio
import digitalio
import gamepadshift
import constants

from light_sensor import LightSensor
from light_sensor import LightSensorOverflow
from battery_monitor import BatteryMonitor

from calibrations import Calibrations
from calibrations import CalibrationsError

from menu_screen import MenuScreen
from error_screen import ErrorScreen
from measure_screen import MeasureScreen

class Mode:
    MEASURE = 0
    MENU    = 1
    ERROR   = 2

class Colorimeter:

    DEFAULT_MEASUREMENTS = [
            'Absorbance', 
            'Transmittance', 
            'Raw Sensor',
            ]

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

        # Load calibrations and populate menu items
        self.mode = Mode.MEASURE
        self.calibrations = Calibrations()
        try:
            self.calibrations.load()
        except CalibrationsError as error: 
            # Unable to load calibrations file or not a dict after loading
            self.error_screen.set_message(error) 
            self.mode = Mode.ERROR
        else:
            # We can load calibration, but detected errors in some calibrations
            if self.calibrations.has_errors:
                error_msg = f'errors found in calibrations file'
                self.error_screen.set_message(error_msg)
                self.mode = Mode.ERROR

        self.menu_items = self.DEFAULT_MEASUREMENTS 
        self.menu_items.extend([k for k in self.calibrations.data])
        self.menu_view_pos = 0
        self.menu_item_pos = 0
        self.measurement_name = self.menu_items[0] 

        # Setup light sensor and blanking data 
        self.light_sensor = LightSensor()
        self.blank_value = 0.0
        self.blank_sensor()
        self.measure_screen.set_not_blanked()
        self.is_blanked = False

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
            led = self.calibrations.led(item)
            if led is None:
                item_text = f'{n0+i} {item}' 
            else:
                item_text = f'{n0+i} {item} ({led})' 
            view_items.append(item_text)
        self.menu_screen.set_menu_items(view_items)
        pos = self.menu_item_pos - self.menu_view_pos
        self.menu_screen.set_curr_item(pos)

    @property
    def measurement_units(self):
        if self.measurement_name in self.DEFAULT_MEASUREMENTS: 
            units = None 
        else:
            units = self.calibrations.units(self.measurement_name)
        return units

    @property
    def raw_sensor_value(self):
        return self.light_sensor.value

    @property
    def transmittance(self):
        transmittance = float(self.raw_sensor_value)/self.blank_value
        return transmittance

    @property
    def absorbance(self):
        absorbance = -ulab.numpy.log10(self.transmittance)
        absorbance = absorbance if absorbance > 0.0 else 0.0
        return absorbance

    @property
    def measurement_value(self):
        if self.measurement_name == 'Transmittance':
            value = self.transmittance
        elif self.measurement_name == 'Absorbance':
            value = self.absorbance
        elif self.measurement_name == 'Raw Sensor':
            value = self.raw_sensor_value
        else:
            value = self.calibrations.apply(
                    self.measurement_name, 
                    self.absorbance
                    )
        return value

    def blank_sensor(self):
        blank_samples = ulab.numpy.zeros((constants.NUM_BLANK_SAMPLES,))
        for i in range(constants.NUM_BLANK_SAMPLES):
            try:
                value = self.raw_sensor_value
            except LightSensorOverflow:
                value = self.light_sensor.max_counts
            blank_samples[i] = value
            time.sleep(constants.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        if buttons:
            # Check debounce timeout has passed
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
                    self.measurement_name = self.menu_items[self.menu_item_pos]
                    self.mode = Mode.MEASURE
                self.update_menu_screen()

            elif self.mode == Mode.ERROR:
                if self.calibrations.has_errors:
                    error_msg = self.calibrations.pop_error()
                    self.error_screen.set_message(error_msg)
                    self.mode = Mode.ERROR
                else:
                    self.mode = Mode.MEASURE

    def check_debounce(self):
        button_dt = time.monotonic() - self.last_button_press
        if button_dt < constants.DEBOUNCE_DT: 
            return False
        else:
            return True

    def run(self):
        while True:
            self.handle_button_press()
            if self.mode == Mode.MEASURE:
                try:
                    self.measure_screen.set_measurement(
                            self.measurement_name, 
                            self.measurement_units, 
                            self.measurement_value
                            )
                except LightSensorOverflow:
                    self.measure_screen.set_overflow(self.measurement_name)
                self.battery_monitor.update()
                battery_voltage = self.battery_monitor.voltage_lowpass
                self.measure_screen.set_bat(battery_voltage)
                self.measure_screen.show()
            elif self.mode == Mode.MENU:
                self.menu_screen.show()
            elif self.mode == Mode.ERROR:
                self.error_screen.show()
            time.sleep(constants.LOOP_DT)

