# Our Destiny
## First off, let me say that this is by no means finished.
Now that that's out of the way, why don't we get started?

## What is this even about?

To put it simply, this is an API client for the Destiny 2 API written in Python. To not, read on:

This was born from my curiosity and love for the game - as much as I feel like I'm doing proper works a disservice by
calling this a "passion project", that is what this is. I love a lot of things about Destiny, and one of those is the
open access to your own data, so I decided to see what I could do with my baseline knowledge of Python, and here we are.

## Where are you planning to go with this?
Well first, I've got to properly implement all of the endpoints in the API, and from there, I don't really know I guess?

For a more detailed list:

* Redo the authentication process to make it more usable in GUI designs
*  Maybe get a better solution to instanced items if we can think of one

* Implement the rest of the "Destiny2" endpoints
* Implement the "GroupV2" endpoints
* Implement the "User" endpoints
* Implement the "Fireteam" endpoints
* Implement the "Forum" endpoints

The exact form of these implementations is something I'm going to decide on when I reach that point - until then I'm
more than willing to hear suggestions or any other feedback in an issue.

## General usage
```python
import ourdestiny
myClient = ourdestiny.d2client("API_KEY", "CLIENT_ID", "CLIENT_SECRET")
guardian = myClient.get_character_object("PLATFORM", 0)
supremacy = guardian.get_instanced_item_by_name("The Supremacy")
guardian.equip_item(supremacy)
```