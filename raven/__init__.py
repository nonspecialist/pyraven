#!/usr/bin/env python

from raven import Raven
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(prog="raven", description="Interrogate the RAVEn USB IHD")
    args = parser.parse_args()

    raven = Raven()
    print raven.get_connection_status()
    print raven.get_summation_delivered()

    limit = 1000
    while limit > 0:
        print raven.get_instantaneous_demand()
        limit -= 1

if __name__ == "__main__":
    main()
