#!/usr/bin/env python

import serial
import threading
import xml.etree.ElementTree as ET

INTERESTING_ELEMENTS = [
    "InstantaneousDemand",
    "CurrentSummationDelivered",
    "ConnectionStatus",
]

class Raven(object):
    """ Represents a USB stick """

    def __init__(self, port='/dev/ttyUSB0'):
        if port is None:
            raise Exception('No serial port provided')

        self.in_fragment = False
        self.serial_ready = False
        self.connection_status = {}
        self.port = port
        self.read_thread = threading.Thread(target=self.read_port)
        ## so it'll get shut down if the main thread exits
        self.read_thread.daemon = True
        self.open_and_init()

    def open_and_init(self):
        self.ser = serial.Serial(self.port, 115200, timeout=None)
        self.read_thread.start()
        self.serial_ready = True
        self.command('initialize')

    def check_connection_status(self):
        if not self.serial_ready:
            raise Exception("Cannot check connection status, serial not ready")

        self.command("get_connection_status")

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
            }
            return

        if "Fail" in status:
            self.connection_status = {
                'is_connected': False,
                'description':  status
            }

    def instantaneous_demand_handler(self, fragment):
        pass

    def summation_handler(self, fragment):
        pass

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
        print "Got a fragment:\n%s" % self.fragment
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

