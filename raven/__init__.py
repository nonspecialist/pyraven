#!/usr/bin/env python

import raven
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(prog="raven", description="Interrogate the RAVEn USB IHD")
    args = parser.parse_args()

if __name__ == "__main__":
    main()
