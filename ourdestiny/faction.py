from ourdestiny import d2progression, d2item


class d2faction():

    """
    The object that represents an in-game faction, and contains all of the data about both that faction and your
    relationship with them.

    :param faction_request_json: The JSON obtained from the API containing live data about the character's status with the faction
    :type faction_request_json: dict
    :param faction_data_json: The JSON obtained from the faction hash given by the API.
    :type faction_data_json: dict
    :param character_object: The d2character object which this object represents the relationship of.
    :type character_object: ourdestiny.d2character

    :ivar name: The name of the faction - this might not always be what you associate the faction with (e.g Brother Vance's faction is "Followers of Osiris)
    :vartype name: string
    :ivar description: The description of the faction
    :vartype description: string
    :ivar icon: The link to the faction's icon
    :vartype icon: string
    :ivar level: The character's current level with this faction
    :vartype level: integer
    :ivar level_cap: The level cap of the faction
    :vartype level_cap: integer
    :ivar next_level_at: The amount of reputation needed to get to the next level
    :vartype next_level_at: integer
    :ivar current_progress: The character's current reputation progress with this faction
    :vartype current_progress: integer
    :ivar daily_progress: The current daily progress with this faction
    :vartype daily_progress: integer
    :ivar daily_limit: The daily limit of progress with this faction
    :vartype daily_limit: integer
    :ivar weekly_progress: The current weekly progress with this faction
    :vartype weekly_progress: integer
    :ivar weekly_limit: The weekly limit of progress with this faction
    :vartype weekly_limit: integer
    :ivar progression: The progression object for this faction's ranks
    :vartype progression: ourdestiny.d2progression
    :ivar character_object: The d2character object that relates to this faction
    :vartype character_object: ourdestiny.d2character
    """

    def __init__(self, faction_request_json, faction_data_json, character_object):
        self.character_object = character_object
        self.name = faction_data_json["displayProperties"]["name"]
        self.description = faction_data_json["displayProperties"]["description"]
        self.level = faction_request_json["level"]
        self.level_cap = faction_request_json["levelCap"]
        self.next_level_at = faction_request_json["nextLevelAt"]
        self.current_progress = faction_request_json["currentProgress"]
        self.daily_progress = faction_request_json["dailyProgress"]
        self.daily_limit = faction_request_json["dailyLimit"]
        self.weekly_progress = faction_request_json["weeklyProgress"]
        self.weekly_limit = faction_request_json["weeklyLimit"]
        if faction_data_json["displayProperties"]["hasIcon"]:
            self.icon = "https://bungie.net" + faction_data_json["displayProperties"]["icon"]
        self.progression = d2progression(self.character_object.profile_object.client_object.get_from_db(faction_data_json["progressionHash"], "Progression"), self.character_object.profile_object)