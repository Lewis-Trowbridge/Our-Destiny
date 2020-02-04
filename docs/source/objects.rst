Objects
=======

d2client
--------

The d2client or just client object has the responsibility of handling processes related to the more technical aspects
of interacting with the API, such as authentication and database handling. The client object also allows you to obtain
a d2character object.

d2character
-----------
This is where things start to get interesting. A d2character object is the object representation of an in-game character
- it holds all of the information tied to them, such as light level, class, as well as both equipped items and items
in a character's inventory, as well as the methods involving equipping items, since these involve equipping an item
*to* a character.

d2item
------
These are the actual items, and as you can probably guess, contain all of the data to represent an in-game item. This
can be anything that you can collect in the game - weapons, ships, sparrows, emotes, and anything else Bungie may add in
future. Items are by default uninstanced - meaning they have generic rather than unique stats, and cannot be equipped.
However, they can be instanced by calling the BecomeInstanced method, allowing you to get more accurate data for these
items.