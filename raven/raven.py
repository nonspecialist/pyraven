#!/usr/bin/env python

import serial
import threading
import xml.etree.ElementTree as ET
import time
import datetime

INTERESTING_ELEMENTS = [
    "InstantaneousDemand",
    "CurrentSummationDelivered",
    "ConnectionStatus",
    "DeviceInfo",
]

# get_* interrogations of the USB device will time out after this many seconds
# if the device doesn't return
DEFAULT_TIMEOUT = 30


def convert_timestamp(tstamp):
    """ Convert a timestamp from the RAVEn format to a datetime object
        The timestamp is actually an offset in seconds from
        midnight on 1-Jan-2000 UTC """

    # This is the number of seconds (epoch seconds) between 1-Jan-1970 and
    # 1-Jan-2000
    OFFSET = 946645200

    return datetime.datetime.fromtimestamp(OFFSET + tstamp)


def hex_to_int(string):
    try:
        result = int(string, 16)
    except Exception:
        result = 0

    return result

def hex_to_mac(string):
    # strip off leading '0x'
    try:
        tmp = string[2:]
        result = ':'.join(
                [tmp[0:2],  tmp[2:4],   tmp[4:6],   tmp[6:8],
                tmp[8:10], tmp[10:12], tmp[12:14], tmp[14:16] ] )
    except:
        result = '00:00:00:00:00:00:00:00'

    return result

class Raven(object):
    """ Represents a USB stick """

    """ Event types """
    EventNone, EventConnectionStatus, EventInstantaneousDemand, EventSummationDelivered, EventDeviceInfo = range(5)

    def __init__(self, port='/dev/ttyUSB0'):
        if port is None:
            raise Exception('No serial port provided')

        self.in_fragment = False
        self.serial_ready = False
        self.connection_status = {}
        self.instantaneous_demand = {}
        self.summation_delivered = {}
        self.device_info = {}
        self.port = port
        self.read_thread = threading.Thread(target=self.read_port)
        # so it'll get shut down if the main thread exits
        self.read_thread.daemon = True
        self.event = self.EventNone
        self.open_and_init()

    def open_and_init(self):
        self.ser = serial.Serial(self.port, 115200, timeout=None)
        self.read_thread.start()
        self.serial_ready = True
        self.command('initialize')

    def factory_reset(self):
        if not self.serial_ready:
            raise Exception("Cannot get device info, serial not ready")

        self.command("factory_reset")

        return True

    def get_device_info(self, timeout=DEFAULT_TIMEOUT):
        if not self.serial_ready:
            raise Exception("Cannot get device info, serial not ready")

        self.device_info_fresh = False
        self.command("get_device_info")

        remaining = float(timeout)
        while remaining > 0:
            if self.device_info_fresh:
                return self.device_info
            time.sleep(0.1)
            remaining -= 0.1

        raise Exception("get_device_info timeout")

    def get_connection_status(self, timeout=DEFAULT_TIMEOUT):
        if not self.serial_ready:
            raise Exception("Cannot check connection status, serial not ready")

        self.connection_status_fresh = False
        self.command("get_connection_status")

        remaining = float(timeout)
        while remaining > 0:
            if self.connection_status_fresh:
                return self.connection_status
            time.sleep(0.1)
            remaining -= 0.1

        raise Exception("get_connection_status timeout")

    def get_instantaneous_demand(self, timeout=DEFAULT_TIMEOUT):
        if not self.serial_ready:
            raise Exception("Cannot get instantaneous demand, serial not ready")

        self.instantaneous_demand_fresh = False
        self.command("get_instantaneous_demand")

        remaining = float(timeout)
        while remaining > 0:
            if self.instantaneous_demand_fresh:
                return self.instantaneous_demand
            time.sleep(0.1)
            remaining -= 0.1

        raise Exception("get_instantaneous_demand timeout")

    def get_summation_delivered(self, timeout=DEFAULT_TIMEOUT):
        if not self.serial_ready:
            raise Exception("Cannot get summation delivered, serial not ready")

        self.summation_delivered_fresh = False
        self.command("get_current_summation_delivered")

        remaining = float(timeout)
        while remaining > 0:
            if self.summation_delivered_fresh:
                return self.summation_delivered
            time.sleep(0.1)
            remaining -= 0.1

        raise Exception("get_summation_delivered timeout")

    # Handlers for the different kind of return messages.
    def connection_status_handler(self, fragment):
        status = fragment.find('Status').text

        if "Connected" == status:
            self.connection_status = {
                'is_connected':  True,
                'link_strength': int(fragment.find('LinkStrength').text, 16),
                'channel':       int(fragment.find('Channel').text),
                'description':   fragment.find('Description').text,
                'extpanid':      int(fragment.find('ExtPanId').text, 16),
                'shortaddr':     fragment.find('ShortAddr').text,
                'status':        status,
            }
        elif "Fail" in status:
            self.connection_status = {
                'is_connected': False,
                'description':  status,
                'status':       status,
            }
        else:
            self.connection_status = {
                'is_connected': False,
                'status':       status,
            }

        self.connection_status_fresh = True
        self.event = self.EventConnectionStatus

    def device_info_handler(self, fragment):
        self.device_info = {
            'device_mac': hex_to_mac(fragment.find('DeviceMacId').text),
            'install_code': hex_to_mac(fragment.find('InstallCode').text),
            'link_key': fragment.find('LinkKey').text,
            'fw_version': fragment.find('FWVersion').text,
            'hw_version': fragment.find('HWVersion').text,
            'image_type': fragment.find('ImageType').text,
            'manufacturer': fragment.find('Manufacturer').text,
            'model_id': fragment.find('ModelId').text,
            'date_code': fragment.find('DateCode').text,
        }

        self.device_info_fresh = True
        self.event = self.EventDeviceInfo

    def instantaneous_demand_handler(self, fragment):
        raw_demand = hex_to_int(fragment.find('Demand').text)
        # with solar the value can go negative
        # this raw_demand is signed int, so the conversion
        #   - Danny ter Haar Feb 2019
        if(raw_demand & 0x80000000):
                raw_demand = -0x100000000 + raw_demand
        multiplier = hex_to_int(fragment.find('Multiplier').text)

        divisor = hex_to_int(fragment.find('Divisor').text)
        demand = float(raw_demand) * multiplier / divisor
        tstamp = convert_timestamp(hex_to_int(fragment.find('TimeStamp').text))

        self.instantaneous_demand = {
            'demand':     demand,
            'raw_demand': raw_demand,
            'multiplier': multiplier,
            'divisor':    divisor,
            'timestamp':  tstamp.isoformat() + 'Z',
        }

        self.instantaneous_demand_fresh = True
        self.event = self.EventInstantaneousDemand

    def summation_handler(self, fragment):
        try:
            tstamp = convert_timestamp(hex_to_int(fragment.find('TimeStamp').text))
        except Exception:
            tstamp = convert_timestamp(0)

        s_delivered = hex_to_int(fragment.find('SummationDelivered').text)
        s_received = hex_to_int(fragment.find('SummationReceived').text)
        multiplier = hex_to_int(fragment.find('Multiplier').text)
        divisor = hex_to_int(fragment.find('Divisor').text)

        if 0 == divisor:
            divisor = 1

        if 0 == multiplier:
            multiplier = 1

        self.summation_delivered = {
            'raw_summation_delivered': s_delivered,
            'raw_summation_received':  s_received,
            'summation_delivered':     float(s_delivered) * multiplier / divisor,
            'summation_received':      float(s_received) * multiplier / divisor,
            'multiplier':              multiplier,
            'divisor':                 divisor,
            'timstamp':                tstamp.isoformat() + 'Z',
        }

        self.summation_delivered_fresh = True
        self.event = self.EventSummationDelivered

    def is_opening_element(self, line):
        for elem in INTERESTING_ELEMENTS:
            if "<" + elem + ">" in line:
                return True

        return False

    def is_closing_element(self, line):
        for elem in INTERESTING_ELEMENTS:
            if "</" + elem + ">" in line:
                return True

        return False

    def handle_fragment(self):
        root = ET.fromstring(self.fragment)

        if root.tag == "ConnectionStatus":
            self.connection_status_handler(root)
        elif root.tag == "InstantaneousDemand":
            self.instantaneous_demand_handler(root)
        elif root.tag == "CurrentSummationDelivered":
            self.summation_handler(root)
        elif root.tag == "DeviceInfo":
            self.device_info_handler(root)

    def read_port(self):
        self.in_element = False
        while True:
            read = self.ser.readline().decode()

            # rather horrid
            if self.is_opening_element(read):
                self.in_fragment = True
                self.fragment = ""

            if self.is_closing_element(read) and self.in_fragment:
                self.in_fragment = False
                self.fragment += read
                self.handle_fragment()

            if self.in_fragment:
                self.fragment += read

    def command(self, command):
        """ Create a 'Command' element and send it to the device """
        cmd = "<Command><Name>%s</Name></Command>\n" % command
        self.ser.write(cmd.encode())

    def long_poll_result(self):
        """ Block until we get an event then return the event object """

        while self.event == self.EventNone:
            time.sleep(0.1)

        if self.event == self.EventConnectionStatus:
            res = self.connection_status
        elif self.event == self.EventInstantaneousDemand:
            res = self.instantaneous_demand
        elif self.event == self.EventSummationDelivered:
            res = self.summation_delivered

        self.event = self.EventNone
        return res
