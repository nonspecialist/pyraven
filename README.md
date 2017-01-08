# PyRAVEn

Some code to talk to the Rainforest Automation "Radio Adapter for Viewing
Energy" (RAVEn).

## Installation

You should be able to install this with `pip`:

1. Clone this repo
1. In the top-level directory (where this README.md is) run
   `pip install --upgrade .`

## Setup

### Prerequisites

You should have already bound (paired) your USB stick to your smart meter.

### Binding/pairing your smart meter

Unlike many other devices, the RAVEn doesn't require a specific "bind
to the meter" command to be issued to it. Instead, your energy
wholesaler or retailer will have to configure your smart meter to bind
with the RAVEn stick. Once the meter has been told to bind to the
device, there will usually be a 10-minute window during which you
simply have to have the USB stick plugged in and close enough to the
meter. The LED will stop flashing, and will turn on solidly once the
stick is bound.

Different retailers and wholesalers will have different methods of
setting up a binding. Some I know of are:

* Powercor/Citipower (Melbourne):
    * They have a "My Energy" portal that you can sign up for at
      https://customermeterdata.portal.powercor.com.au/customermeterdata/
      (correct as of Jan 2017). Once you've signed up, there's a
      pulldown from your name that allows you to "Manage my HAN
      devices", wherein you can bind your RAVEn to the meter.

## Documentation

The XML protocol specification can be [downloaded from
Rainforest Automation](http://www.rainforestautomation.com/sites/default/files/download/rfa-z106/raven_xml_api_r127.pdf)

## Other works

There are other open-source projects which cover some of the same
ground. My intents in re-inventing this wheel were to provide a more
complete and standardised Python implementation that could be used as a
library by others, instead of the fairly implementation-specific versions
already out there.

* [Entropy](https://github.com/phubbard/entropy)
    * Python
    * streams data to plot.ly
* [python-raven](https://github.com/frankp/python-raven)
    * Python
    * publishes data to a Mosquitto server (MQTT)
* [node-raven](https://github.com/stormboy/node-raven)
    * NodeJS
    * publishes to an MQTT server

