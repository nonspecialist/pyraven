PyRAVEn
=======

|travis-badge| |pypi-badge|

.. |travis-badge| image:: https://img.shields.io/travis/nonspecialist/pyraven.svg
   :target: https://travis-ci.org/nonspecialist/pyraven
   :alt: Travis build badge for pyraven

.. |pypi-badge| image:: https://img.shields.io/pypi/v/pyraven.svg
   :target: https://pipy.python.org/pypi/pyraven
   :alt: PyPI version badge

Some code to talk to the Rainforest Automation "Radio Adapter for Viewing
Energy" (RAVEn).

Installation
------------

The easiest way would be ``pip install pyraven``

You could also install direct from this repository:

#. Clone this repo
#. In the top-level directory (where this ``README.rst`` is) run
   ``pip install --upgrade .``

Setup
-----

Prerequisites
~~~~~~~~~~~~~

You should have already bound (paired) your USB stick to your smart meter.

Binding/pairing your smart meter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    * Use the portal at https://connect.ausnetservices.com.au/webui/
      to bind your device
* United Energy:
    * they have a *startlingly similar* portal to Jemena, located at
      https://energyeasy.ue.com.au/ that you can use to set up a
      binding

Usage
-----

There's a simple CLI, used to assist in the development of the library
itself. Once your USB stick is set up and bound to your meter, you
can use the CLI to monitor the current instantaneous demand reported
by your meter:

.. code:: shell

    localhost$ raven
    {'status': 'Connected', 'shortaddr': '0xd131', 'link_strength': 100, 'extpanid': 1234567890123456L, 'is_connected': True, 'channel': 11, 'description': 'Successfully Joined'}
    {'divisor': 1000, 'summation_delivered': 2220.575, 'raw_summation_received': 0, 'timstamp': '2018-03-27T02:45:45Z', 'raw_summation_delivered': 2220575, 'multiplier': 1, 'summation_received': 0.0}
    {'divisor': 1000, 'summation_delivered': 2220.575, 'raw_summation_received': 0, 'timstamp': '2018-03-27T02:45:45Z', 'raw_summation_delivered': 2220575, 'multiplier': 1, 'summation_received': 0.0}
    {'timestamp': '2018-03-27T02:47:56Z', 'raw_demand': 142, 'multiplier': 1, 'divisor': 1000, 'demand': 0.142}
    ...

and so on.

Instantaneous readings show the current demand, and the summation
includes power delivered to the grid (eg from a PV array).

The frequency of different types of data delivery are set
by the schedule in the USB stick. By default, they are:

- Instantaneous demand: 8 seconds
- Summation: 240 seconds
- Profile data: disabled
- Scheduled prices: 90 seconds
- Price: 90 seconds
- Messages: 120 seconds
- Time: 900 seconds (reports the current time known to the meter)

However, the meter I have has no pricing data (this seems to be common
in Australia, because wholesalers and retailers are different
entities, and the retailer applies the pricing based on their own
peculiar calculations from the raw consumption data) and so the price
elements are never emitted.

Similarly, if there are no messages to be consumed, the RAVEn will not
emit a message element.

In practice, this means that you'll usually only get the instantaneous
demand and summation outputs.

Documentation
-------------

The XML protocol specification used to be be `available from
Rainforest Automation <http://www.rainforestautomation.com/sites/default/files/download/rfa-z106/raven_xml_api_r127.pdf>`__
but that link no longer works. I've included the version that I
had previously downloaded under the `docs` directory

Other works
-----------

There are other open-source projects which cover some of the same
ground. My intents in re-inventing this wheel were to provide a more
complete and standardised Python implementation that could be used as a
library by others, instead of the fairly implementation-specific versions
already out there.

* `Entropy <https://github.com/phubbard/entropy>`__
    * Python
    * streams data to plot.ly
* `python-raven <https://github.com/frankp/python-raven>`__
    * Python
    * publishes data to a Mosquitto server (MQTT)
* `node-raven <https://github.com/stormboy/node-raven>`__
    * NodeJS
    * publishes to an MQTT server
