import ourdestiny
from enum import IntEnum


class d2progression:

    """
    The object that represents an in-game "progression", meaning any ranking or reputation system, such as Glory Ranks or destination factions.

    :param progression_db_json: The JSON obtained from the database containing the data about the progression
    :type progression_db_json:
    :param profile_object_in: The profile object that owns this progression
    :type profile_object_in: ourdestiny.d2profile

    :ivar name: The name of the progression
    :vartype name: string
    :ivar description: The description of the progression
    :vartype description: string
    :ivar units: The units used for how this progression counts progress
    :vartype units: string
    :ivar steps: A list of dicts each with information about steps for progressing through ranks of progression, such as individual glory ranks
    :vartype steps: List[dict]
    :ivar reward_items: A list of reward items
    :ivar visible: A boolean variable displaying whether this should be visible or not
    :type visible: bool
    :ivar scope: The scope of the progression
    :type scope: string
    """

    def __init__(self, progression_db_json, profile_object_in):
        self.name = progression_db_json["displayProperties"]["name"]
        self.description = progression_db_json["displayProperties"]["description"]
        self.visible = progression_db_json["visible"]
        self.scope = ProgressionScope(progression_db_json["scope"])
        self.units = progression_db_json["displayProperties"]["displayUnitsName"]
        self.steps = progression_db_json["steps"]
        self.reward_items = []
        for reward_item in progression_db_json["rewardItems"]:
            self.reward_items.append(ProgressionRewardItem(reward_item, profile_object_in))


class ProgressionRewardItem(ourdestiny.d2item):

    """
    A reward item from a progression, inheriting from ourdestiny.d2item with extra attributes provided

    :param progression_item_json: The JSON data of the item obtained from the API
    :type progression_item_json: dict
    :param profile_object_in: The object was used to create this item
    :type profile_object_in: ourdestiny.d2profile

    :ivar rewarded_at_level: The level of the progression at which this item is rewarded
    :type rewarded_at_level: integer
    :ivar acquisition_behaviour: How the item will behave when it is acquired
    :type acquisition_behaviour: string
    """

    def __init__(self, progression_item_json, profile_object_in):
        super().__init__(progression_item_json, profile_object_in)
        self.rewarded_at_level = progression_item_json["rewardedAtProgressionLevel"]
        self.acquisition_behaviour = ProgressionRewardItemAcquisitionBehaviour(progression_item_json["acquisitionBehavior"])


class ProgressionRewardItemAcquisitionBehaviour(IntEnum):

    """An enumeration. See https://bungie-net.github.io/multi/schema_Destiny-DestinyProgressionRewardItemAcquisitionBehavior.html"""

    #: Means that as soon as the progression is completed, the item will be acquired.
    Instant = 0
    #: Means that player action is required to claim the item.
    PlayerClaimRequired = 1


class ProgressionScope(IntEnum):

    """An enumeration. See https://bungie-net.github.io/multi/schema_Destiny-DestinyProgressionScope.html"""

    Account = 0
    Character = 1
    Clan = 2
    Item = 3
    ImplicitFromEquipment = 4
    Mapped = 5
    MappedAggregate = 6
    MappedStat = 7
    MappedUnlockValue = 8
