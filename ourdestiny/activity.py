import ourdestiny

class d2activity:

    """
    A class used to represent an activity, selectable from the director

    :param activity_json: The JSON obtained from the database containing information about the activity
    :type activity_json:
    :param profile_object: The profile object used to obtain this object
    :type profile_object: ourdestiny.d2profile

    :ivar name: The name of the activity
    :vartype name: string
    :ivar description: The description of the activity
    :vartype description: string
    :ivar icon: The URL of the icon for the activity, if it has one
    :vartype icon: string
    :ivar hash: The hash number of the activity
    :vartype hash: string
    :ivar is_pvp: Displays whether or not the activity is a PvP activity
    :vartype is_pvp: bool
    :ivar is_playlist: Displays whether or not the activity is a playlist
    :vartype is_playlist: bool
    :ivar activity_level: The recommended level to play this activity - somewhat outdated since Forsaken
    :vartype activity_level: integer
    :ivar light_level: The recommended light level to play this activity
    :vartype light_level: integer
    :ivar tier: The difficulty tier of the activity
    :vartype tier: integer
    :ivar pgcr_image: The URL to the post-game carnage report image for this activity
    :vartype pgcr_image: string
    :ivar rewards: The potential rewards for this activity, split into tiers as given by the API
    :vartype rewards: List[List[ourdestiny.d2item]]
    """

    def __init__(self, activity_json, profile_object):
        self.name = activity_json["displayProperties"]["name"]
        self.description = activity_json["displayProperties"]["description"]
        self.hash = activity_json["hash"]
        self.is_pvp = activity_json["isPvP"]
        self.is_playlist = activity_json["isPlaylist"]
        self.activity_level = activity_json["activityLevel"]
        self.tier = activity_json["tier"]
        self.light_level = activity_json["activityLightLevel"]
        if activity_json["displayProperties"]["hasIcon"]:
            self.icon = "https://bungie.net" + activity_json["displayProperties"]["icon"]
        else:
            self.icon = None
        self.pgcr_image = "https://bungie.net" + activity_json["pgcrImage"]
        self.rewards = []
        for reward_tier in activity_json["rewards"]:
            reward_tier_list = []
            self.rewards.append(reward_tier_list)
            for reward_item in reward_tier["rewardItems"]:
                reward_tier_list.append(ourdestiny.d2item(reward_item, profile_object))
        self.activity_type = d2activitytype(profile_object.client_object.get_from_db(activity_json["activityTypeHash"], "ActivityType"))


class d2activitytype:

    """
    A class used to represent an activity type

    :param activity_type_json: The JSON of the activity type obtained from the database
    :type activity_type_json: dict

    :ivar name: The name of the activity type
    :vartype name: string
    :ivar description: The description of the activity type
    :vartype description: string
    :ivar hash: The hash of the activity type
    :vartype hash: integer
    :ivar icon: The URL of the icon, if this activity type has one
    :vartype icon: string
    """

    def __init__(self, activity_type_json):
        self.name = activity_type_json["displayProperties"]["name"]
        try:
            self.description = activity_type_json["displayProperties"]["description"]
        except KeyError:
            self.description = None
        self.hash = activity_type_json["hash"]
        if activity_type_json["displayProperties"]["hasIcon"]:
            self.icon = "https://bungie.net" + activity_type_json["displayProperties"]["icon"]
        else:
            self.icon = None