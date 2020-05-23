import datetime


class bungienetuser():

    """
    A class representing a Bungie.net user account

    :param bungienet_json: A JSON file obtained from the Bungie API for bungienet users
    :type bungienet_json: dict

    :ivar membership_id: The membership ID for this bungienet user
    :type membership_id: string
    :ivar unique_name: The unique name of the bungienet user
    :type unique_name: string
    :ivar display_name: The display name of the bungienet user
    :type display_name: string
    :ivar about: The about text of the bungienet user
    :type about: string
    :ivar status_text: The status text of the bungienet user
    :type status_text: string
    :ivar first_access: The date and time when the account was first accessed
    :type first_access: datetime.datetime
    :ivar last_update: The date and time when the account was last updated
    :type last_update: datetime.datetime
    :ivar membership_types: A dictionary with keys relating to each of the membership type enums, containing the display name of the user on that platform if they have one, and a None if they do not
    :type membership_types: dict
    """

    def __init__(self, bungienet_json):
        self.membership_id = bungienet_json["membershipId"]
        self.unique_name = bungienet_json["uniqueName"]
        self.display_name = bungienet_json["displayName"]
        self.about = bungienet_json["about"]
        self.status_text = bungienet_json["statusText"]
        self.first_access = datetime.datetime.strptime(bungienet_json["firstAccess"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.last_update = datetime.datetime.strptime(bungienet_json["lastUpdate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.membership_types = {}
        try:
            self.membership_types["1"] = bungienet_json["xboxDisplayName"]
        except KeyError:
            self.membership_types["1"] = None
        try:
            self.membership_types["2"] = bungienet_json["psnDisplayName"]
        except KeyError:
            self.membership_types["2"] = None
        try:
            self.membership_types["3"] = bungienet_json["steamDisplayName"]
        except KeyError:
            self.membership_types["3"] = None
        try:
            self.membership_types["4"] = bungienet_json["blizzardDisplayName"]
        except KeyError:
            self.membership_types["4"] = None
        try:
            self.membership_types["5"] = bungienet_json["stadiaDisplayName"]
        except KeyError:
            self.membership_types["5"] = None
