#!/usr/bin/env python

from raven import Raven
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(prog="raven", description="Interrogate the RAVEn USB IHD")
    args = parser.parse_args()

    raven = Raven()
    time.sleep(1)
    raven.command('get_connection_status')
    time.sleep(100)

if __name__ == "__main__":
    main()
