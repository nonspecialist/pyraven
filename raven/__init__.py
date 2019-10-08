#!/usr/bin/env python

from . import raven
from . import _version
import argparse
import sys
import json


def main():
    parser = argparse.ArgumentParser(prog="raven",
                                     description="Interrogate the RAVEn USB IHD")
    parser.add_argument('--port', '-p',
                        help='Serial port of the USB stick [/dev/ttyUSB0]',
                        default="/dev/ttyUSB0")
    parser.add_argument('--limit', '-l',
                        help='Count of events to consume before stopping [1000]',
                        default=1000)
    parser.add_argument('--version', '-V',
                        action='version',
                        version='%(prog)s {version}'.format(version=_version.__version__))
    parser.add_argument('--deviceinfo', '-D',
                        action='store_true',
                        default=False,
                        help='Dump out device info')

    parser.add_argument('--factory-reset',
                        action='store_true',
                        default=False,
                        help='FACTORY RESET -- for binding to new meter')

    parser.add_argument('--yes-really',
                        action='store_true',
                        default=False,
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    raven_usb = raven.Raven(vars(args)['port'])
    if (vars(args)['deviceinfo']):
        print(json.dumps(raven_usb.get_device_info(), indent=4))
        sys.exit(0)

    if (vars(args)['factory_reset']):
        if not (vars(args)['yes_really']):
            print("Will not factory reset: re-run with hidden argument --yes-really")
            sys.exit(1)
        else:
            print("FACTORY RESET IN PROGRESS")
            if raven_usb.factory_reset():
                sys.exit(0)
            else:
                sys.exit(1)

    print(json.dumps(raven_usb.get_connection_status()))
    print(json.dumps(raven_usb.get_summation_delivered()))

    # just wait for a while, because the scheduler inside the stick delivers
    # instantaneous demand automatically
    limit = int(vars(args)['limit']) or -1
    while limit < 0 or limit > 0:
        print(json.dumps(raven_usb.long_poll_result()))
        if limit > 0:
            limit -= 1


if __name__ == "__main__":
    main()
