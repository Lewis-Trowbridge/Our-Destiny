

class d2progression():

    """
    The object that represents an in-game "progression", meaning any ranking or reputation system, such as Glory Ranks or destination factions.

    :param progression_db_json: The JSON obtained from the database containing the data about the progression
    :type progression_db_json:
    :ivar name: The name of the progression
    :vartype name: string
    :ivar description: The description of the progression
    :vartype description: string
    :ivar units: The units used for how this progression counts progress
    :vartype units: string
    :ivar steps: A list of dicts each with information about steps for progressing through ranks of progression, such as individual glory ranks
    :vartype steps: list
    """

    def __init__(self, progression_db_json):
        self.name = progression_db_json["displayProperties"]["name"]
        self.description = progression_db_json["displayProperties"]["description"]
        self.units = progression_db_json["displayProperties"]["displayUnitsName"]
        self.steps = progression_db_json["steps"]
