from ourdestiny import d2progression, d2item


class d2faction():

    """
    The object that represents an in-game faction, and contains all of the data about both that faction and your
    relationship with them.

    :param faction_json: The JSON obtained from the faction hash given by the API.
    :type faction_json: dict
    :param character_object: The d2character object which this object represents the relationship of.
    :type character_object: ourdestiny.d2character
    :ivar name: The name of the faction - this might not always be what you associate the faction with (e.g Brother Vance's faction is "Followers of Osiris)
    :vartype name: string
    :ivar description: The description of the faction
    :vartype description: string
    :ivar icon: The link to the faction's icon
    :vartype icon: string
    :ivar progression: The progression object for this faction's ranks
    :vartype progression: ourdestiny.d2progression
    :ivar character_object: The d2character object that relates to this faction
    :vartype character_object: ourdestiny.d2character
    """

    def __init__(self, faction_json, character_object):
        self.character_object = character_object
        self.name = faction_json["displayProperties"]["name"]
        self.description = faction_json["displayProperties"]["description"]
        if faction_json["displayProperties"]["hasIcon"]:
            self.icon = "https://bungie.net" + faction_json["displayProperties"]["icon"]
        self.progression = d2progression(self.character_object.profile_object.client_object.get_from_db(faction_json["progressionHash"], "Progression"), self.character_object.profile_object)