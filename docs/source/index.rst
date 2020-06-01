.. Our Destiny documentation master file, created by
   sphinx-quickstart on Tue Feb  4 13:03:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. _objects:

Welcome to Our Destiny's documentation!
=======================================

This project exists to allow for the use of the Destiny 2 API in Python, using objects to represent the ways in which
data and actions are used in the game, with characters and items being the most important, and therefore make the
process as logical and easy-to-understand as possible.

To understand more about these objects, go to the :doc:`objects` page

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   intro
   objects
   client
   bungienetuser
   profile
   character
   activity
   item
   faction
   progression
   season

Installation
------------

1. cd to project directory
2. pip install .

Getting started
---------------

.. code-block:: python
   :linenos:

   import ourdestiny
   myClient = ourdestiny.d2client("API_KEY", "CLIENT_ID", "CLIENT_SECRET")
   myProfile = myClient.get_my_profile("PLATFORM")
   guardian = myProfile.characters[0]
   supremacy = guardian.get_instanced_item_by_name("The Supremacy")
   guardian.equip_item(supremacy)


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
