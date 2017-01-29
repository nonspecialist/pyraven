#!/usr/bin/env python

from raven import Raven
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(prog="raven", description="Interrogate the RAVEn USB IHD")
    parser.add_argument('--port', '-p', help='Serial port of the USB stick [/dev/ttyUSB0]', default="/dev/ttyUSB0")
    args = parser.parse_args()

    raven = Raven(vars(args)['port'])
    print raven.get_connection_status()
    print raven.get_summation_delivered()

    # just wait for a while, because the scheduler inside the stick delivers
    # instantaneous demand automatically
    limit = 1000
    while limit > 0:
        print raven.long_poll_result()
        limit -= 1

if __name__ == "__main__":
    main()
