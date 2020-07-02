import ourdestiny
from enum import IntEnum


class d2progression(ourdestiny.d2displayproperties):

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
    :vartype reward_items: list[ourdestiny.ProgressionRewardItem]
    :ivar visible: A boolean variable displaying whether this should be visible or not
    :vartype visible: bool
    :ivar scope: The scope of the progression
    :vartype scope: ProgressionScope
    :ivar daily_progress: The current daily progress made on this progression
    :vartype daily_progress: integer
    :ivar daily_limit: The limit of progress that can be made on this progression in a day
    :vartype daily_limit: integer
    :ivar weekly_progress: The current weekly progress made on this progression
    :vartype weekly_progress: integer
    :ivar weekly_limit: The limit of progress that can be made on this progression in a week
    :vartype weekly_limit: integer
    :ivar current_progress: The current total progress made on this progression
    :vartype current_progress: integer
    :ivar level: The current level of this progression
    :vartype level: integer
    :ivar level_cap: The level cap of this progression
    :vartype level_cap: integer
    :ivar step_index: The index of the current step
    :vartype step_index: integer
    :ivar current_step: If it is accessible, the step the character is currently on
    :vartype current_step: dict
    :ivar current_reset_count: If the progression can be reset, the number of times it has been reset
    :vartype current_reset_count: integer
    :ivar season_resets: Th
    """

    def __init__(self, progression_db_json, profile_object_in, progression_live_json=None):
        super().__init__(progression_db_json["displayProperties"])
        self.visible = progression_db_json["visible"]
        self.scope = ProgressionScope(progression_db_json["scope"])
        self.units = progression_db_json["displayProperties"]["displayUnitsName"]
        self.steps = progression_db_json["steps"]
        self.reward_items = []
        for reward_item in progression_db_json["rewardItems"]:
            self.reward_items.append(ProgressionRewardItem(reward_item, profile_object_in))
        if progression_live_json is not None:
            self.daily_progress = progression_live_json["dailyProgress"]
            self.daily_limit = progression_live_json["dailyLimit"]
            self.weekly_progress = progression_live_json["weeklyProgress"]
            self.weekly_limit = progression_live_json["weeklyLimit"]
            self.current_progress = progression_live_json["currentProgress"]
            self.level = progression_live_json["level"]
            self.level_cap = progression_live_json["levelCap"]
            self.step_index = progression_live_json["stepIndex"]
            try:
                self.current_step = self.steps[self.step_index]
            except IndexError:
                self.current_step = None
            self.progress_to_next_level = progression_live_json["progressToNextLevel"]
            self.next_level_at = progression_live_json["nextLevelAt"]
            try:
                self.current_reset_count = progression_live_json["currentResetCount"]
            except KeyError:
                self.current_reset_count = None
        else:
            self.daily_progress = None
            self.daily_limit = None
            self.weekly_progress = None
            self.weekly_limit = None
            self.current_progress = None
            self.level = None
            self.level_cap = None
            self.step_index = None
            self.current_step = None
            self.progress_to_next_level = None
            self.next_level_at = None
            self.current_reset_count = None
            self.season_resets = None


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
