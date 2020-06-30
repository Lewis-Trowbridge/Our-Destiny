import ourdestiny


class d2lore(ourdestiny.d2displayproperties):

    """
    A class used to contain information about lore in the game

    :param lore_json: A JSON obtained from the database containing lore data
    :type lore_json: dict

    :ivar name: The name of the lore piece
    :vartype name: string
    :ivar description: The description of the lore piece - this is where the main text of the lore will be
    :vartype description: string
    :ivar subtitle: The subtitle of the lore piece - normally only used on lore tabs on items
    :vartype subtitle: string
    :ivar hash: The hash of the lore piece
    :vartype hash: integer
    """

    def __init__(self, lore_json):
        super().__init__(lore_json["displayProperties"])
        self.subtitle = lore_json["subtitle"]
        self.hash = lore_json["hash"]
