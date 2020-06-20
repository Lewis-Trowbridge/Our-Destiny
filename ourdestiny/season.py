import datetime
import ourdestiny


class d2season(ourdestiny.d2displayproperties):

    """
    A class used to represent a season

    :param season_json: A JSON obtained from the database from the season hash
    :type season_json: dict
    :param profile_object: The profile object used to obtain this season object
    :type profile_object: ourdestiny.d2profile

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
    :ivar artifact_item: The artifact of this season
    :vartype artifact_item: ourdestiny.d2item
    """

    def __init__(self, season_json, profile_object):
        super().__init__(season_json["displayProperties"])
        self.season_number = season_json["seasonNumber"]
        self.start_date = datetime.datetime.strptime(season_json["startDate"], "%Y-%m-%dT%H:%M:%SZ")
        try:
            self.end_date = datetime.datetime.strptime(season_json["endDate"], "%Y-%m-%dT%H:%M:%SZ")
        except KeyError:
            self.end_date = None
        self.season_pass = d2seasonpass(profile_object.client_object.get_from_db(season_json["seasonPassHash"], "SeasonPass"), profile_object)
        # TODO: Create a class that inherits from item for artifacts for special attributes
        self.artifact_item = ourdestiny.d2item({"itemHash": season_json["artifactItemHash"], "quantity": 0}, profile_object)


class d2seasonpass(ourdestiny.d2displayproperties):

    """
    A class used to represent a season pass

    :param season_pass_json: A JSON obtained from the database from the season pass hash
    :type season_pass_json: dict
    :param profile_object: The profile object used to obtain this season pass object
    :type profile_object: ourdestiny.d2profile

    :ivar name: The name of the season pass
    :type name: string
    :ivar hash: The hash of the season pass
    :type hash: integer
    :ivar reward_progression: The progression for the initial 1-100 levels of the season pass
    :type reward_progression: ourdestiny.d2progression
    :ivar prestige_progression: The progression for above rank 100 on the season pass
    :type prestige_progression: ourdestiny.d2progression
    """

    def __init__(self, season_pass_json, profile_object):
        super().__init__(season_pass_json["displayProperties"])
        self.hash = season_pass_json["hash"]
        if season_pass_json["rewardProgressionHash"] != 0:
            self.reward_progression = ourdestiny.d2progression(profile_object.client_object.get_from_db(season_pass_json["rewardProgressionHash"], "Progression"), profile_object)
        else:
            self.reward_progression = None
        if season_pass_json["prestigeProgressionHash"] != 0:
            self.prestige_progression = ourdestiny.d2progression(profile_object.client_object.get_from_db(season_pass_json["prestigeProgressionHash"], "Progression"), profile_object)
        else:
            self.prestige_progression = None
