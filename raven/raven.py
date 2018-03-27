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


class Raven(object):
    """ Represents a USB stick """

    """ Event types """
    EventNone, EventConnectionStatus, EventInstantaneousDemand, EventSummationDelivered = range(4)

    def __init__(self, port='/dev/ttyUSB0'):
        if port is None:
            raise Exception('No serial port provided')

        self.in_fragment = False
        self.serial_ready = False
        self.connection_status = {}
        self.instantaneous_demand = {}
        self.summation_delivered = {}
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

    def instantaneous_demand_handler(self, fragment):
        raw_demand = hex_to_int(fragment.find('Demand').text)
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
        self.ser.write(cmd)

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
