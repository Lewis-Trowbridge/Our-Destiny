class OurDestinyError(Exception):

    """Base exception class for custom exceptions"""
    pass


class ItemNotInBucket(OurDestinyError):

    """
    Exception for when an item is in a different bucket than expected

    :ivar item: The item involved in the mixup
    :vartype item: ourdestiny.d2item
    """

    def __init__(self, item):
        self.item = item
        self.message = "Item " + item.name + " is not in the bucket expected."
        super().__init__(self.message)


class ItemDoesNotBelongToCharacter(OurDestinyError):

    """
    Exception for when an operation performed on an item involving the owner of that item is faced with another character, or that item has no owner

    :ivar item: The item attempting to be equipped
    :vartype item: ourdestiny.d2item
    :ivar character: The character attempting to equip the item
    :vartype character: ourdestiny.d2character
    """

    def __init__(self, item, character):
        self.item = item
        self.character = character
        self.message = "Item " + item.name + " does not belong to character " + character.character_id+"."
        super().__init__(self.message)


class NoRoomInDestination(OurDestinyError):

    """
    Exception for an operation where an item is moved, but there is no room for that item in the destination

    :ivar item: The item in question
    :vartype item: ourdestiny.d2item
    :ivar message: The error message given by the API
    :vartype message: string
    """

    def __init__(self, item, message):
        self.item = item
        self.message = message
        super().__init__(self.message)


class ItemNotFound(OurDestinyError):

    """
    Exception for when an item is referenced but does not appear to exist

    :ivar item: The item in question
    :vartype item: ourdestiny.d2item
    :ivar message: The error message obtained from the API
    :vartype message: string
    """

    def __init__(self, item, message):
        self.item = item
        self.message = message
        super().__init__(self.message)


class ItemNotInstanced(OurDestinyError):

    """
    Exception for when an operation requires an item be instanced, but it is not
    """

    def __init__(self, item):
        self.item = item
        self.message = "Item " + item.name + " is not instanced."
        super().__init__(self.message)


class ItemCannotBeInstanced(OurDestinyError):
    """
    Exception for when an attempt is made to instance an item, but it has no instance ID, and cannot be instanced
    """

    def __init__(self, item):
        self.item = item
        self.message = "Item " + item.name + " cannot be instanced."


class StatesDoNotMatch(OurDestinyError):

    """
    Exception for when the cross-site forgery mitigation test fails
    """
    pass
