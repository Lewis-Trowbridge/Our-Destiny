import datetime


class d2season():

    """
    A class used to represent a season

    :param season_json: A JSON obtained from the database from the season hash
    :type season_json: dict
    :param client_object: The client object used to obtain this season object
    :type client_object: ourdestiny.d2client

    :ivar name: The name of the season
    :vartype name: string
    :ivar description: The description of the season
    :vartype description: string
    :ivar season_number: The season number
    :vartype season_number: integer
    :ivar start_date: The start date of this season
    :vartype start_date: datetime
    :ivar end_date: The end date of this season - can be none where the season's end date is not confirmed yet
    :vartype end_date: datetime

    """

    def __init__(self, season_json, client_object):
        self.name = season_json["displayProperties"]["name"]
        self.description = season_json["displayProperties"]["description"]
        self.season_number = season_json["seasonNumber"]
        self.start_date = datetime.datetime.strptime(season_json["startDate"], "%Y-%m-%dT%H:%M:%SZ")
        try:
            self.end_date = datetime.datetime.strptime(season_json["endDate"], "%Y-%m-%dT%H:%M:%SZ")
        except KeyError:
            self.end_date = None
