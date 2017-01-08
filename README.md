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
* Jemena (Melbourne):
    * Use their portal at https://electricityoutlook.jemena.com.au/ to
      bind your USB device
* AusNet Services:
    * unknown
* United Energy:
    * they have a _startlingly similar_ portal to Jemena, located at
      https://energyeasy.ue.com.au/ that you can use to set up a
      binding

## Usage

There's a simple CLI, used to assist in the development of the library
itself. Once your USB stick is set up and bound to your meter, you
can use the CLI to monitor the current instantaneous demand reported
by your meter:

```shell
localhost$ raven monitor
2017-01-08T12:19:19+11:00 Instantaneous 1.915
2017-01-08T12:19:27+11:00 Instantaneous 1.893
2017-01-08T12:19:35+11:00 Summation 44502.369 0.0
2017-01-08T12:19:43+11:00 Instantaneous 1.721
```

and so on.

Instantaneous readings show the current demand, and the summation
includes power delivered to the grid (eg from a PV array).

The frequency of different types of data delivery are set
by the schedule in the USB stick. By default, they are:

* Instantaneous demand: 8 seconds
* Summation: 240 seconds
* Profile data: disabled
* Scheduled prices: 90 seconds
* Price: 90 seconds
* Messages: 120 seconds
* Time: 900 seconds (reports the current time known to the meter)

However, the meter I have has no pricing data (this seems to be common
in Australia, because wholesalers and retailers are different
entities, and the retailer applies the pricing based on their own
peculiar calculations from the raw consumption data) and so the price
elements are never emitted.

Similarly, if there are no messages to be consumed, the RAVEn will not
emit a message element.

In practice, this means that you'll usually only get the instantaneous
demand and summation outputs.

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

