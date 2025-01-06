# touch_setup.py Customise for your hardware config
# based on:
#   * https://github.com/clach04/micropython-touch/blob/master/setup_examples/ili9341_xpt2046_esp32.py
#   * https://github.com/peterhinch/micropython-nano-gui/pull/80 - Sunton ESP32-2432S028 aka CYD setup support - ili9341_esp32_cyd.py

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on Sunton ESP32-2432S028, also known as CYD
# See https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display/ for more details
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING for CYD
# ESP   SSD
# 3v3   Vin
# Gnd   Gnd
# IO02  DC
# IO15  CS
# IO15  Rst
# IO14  CLK  Hardware SPI1
# IO13  DATA (AKA SI MOSI)

from machine import Pin, PWM, SPI, SoftSPI
import gc

# *** Choose your color display driver here ***
# ili9341 specific driver
from drivers.ili93xx.ili9341 import ILI9341 as SSD

PIN_sck = 14
PIN_mosi = 13
# miso - doesn't need to be explictly set
PIN_dc = 2
PIN_cs = 15
PIN_rst = 15


pdc = Pin(PIN_dc, Pin.OUT, value=0)  # Arbitrary pins
pcs = Pin(PIN_cs, Pin.OUT, value=1)
prst = Pin(PIN_rst, Pin.OUT, value=1)

# Kept as ssd to maintain compatability
gc.collect()  # Precaution before instantiating framebuf
#spi = SPI(1, 40_000_000, sck=Pin(PIN_sck), mosi=Pin(PIN_mosi))  # default miso. 40Mhz out of spec but seems to work fine
spi = SPI(1, 10_000_000, sck=Pin(PIN_sck), mosi=Pin(PIN_mosi))  # default miso


# NOTE on CYD1 clock is upside down.
# With power usb bottom right from front, clock is bottom right hand and upside down
# setting usd to True will correct this - https://github.com/peterhinch/micropython-nano-gui/blob/master/DRIVERS.md#32-drivers-for-ili9341
# TODO for CYD2 probably need to pass in height=320, width=240 (i.e. transposed compared with default and CYD1)
usd = False  # Default
usd = True

ssd = SSD(spi, dc=pdc, cs=pcs, rst=prst, usd=usd)

# on CYD need to turn on backlight to see anything
backlight_percentage = 50
backlight = Pin(21, Pin.OUT)
backlight_pwm = PWM(backlight)
#backlight.on()  # PWM preferred instead of on/off
#backlight_pwm.duty(1023)  # 100%
#backlight_pwm.duty(512)  # 50%
# TODO ensure backlight_percentage is 0-100
backlight_pwm.duty(int(backlight_percentage * 10.23))  # 1023 / 100


from gui.core.tgui import Display, quiet

# quiet()  # Comment this out for periodic free RAM messages
from touch.xpt2046 import XPT2046

# touch not yet working...
# Touch configuration
#sspi = SoftSPI(baudrate=1_000_000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
#sspi = SoftSPI(baudrate=500_000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
sspi = SoftSPI(sck=Pin(25), mosi=Pin(32), miso=Pin(39))
#self._touch = Touch(sspi, cs=Pin(33), int_pin=Pin(36), int_handler=self._touch_handler)
#touch = Touch(touch_spi, cs=Pin(33), int_pin=Pin(36), int_handler=touchscreen_press)


#               spi, cspin, ssd, *, alen=10):
tpad = XPT2046(sspi, Pin(33, Pin.OUT, value=1), ssd)  # did not seem to work
#tpad = XPT2046(sspi, Pin(33), ssd)
# To create a tpad.init line for your displays please read SETUP.md
# tpad.init(240, 320, 151, 151, 4095, 4095, True, True, True)
# See section, "Dead zones"
tpad.init(240, 320, 151, 151, 4095, 4095, True, True, True)  # TEST, not sure going to work due to missing inteript for screen conflict on CYD

# instantiate a Display
display = Display(ssd, tpad)
