import ourdestiny


class d2profile():

    """
    A class used to represent a Destiny 2 profile, or a player, which owns multiple characters and several profile-level attributes

    :param profile_json: A JSON obtained from GetProfile with the Profiles enumerator
    :type profile_json: dict
    :param client_object: The client object used to obtain this profile object
    :type client_object: ourdestiny.d2client

    :ivar client_object: A link to the client object being used for API authentication
    :vartype client_object: ourdestiny.d2client
    :ivar display_name: The display name for this profile
    :vartype display_name: string
    :ivar membership_type: The membership type enumerator used to represent the platform this profile is registered on#
    :vartype membership_type: integer
    :ivar membership_id: The membership ID for this profile
    :vartype membership_id: string
    :ivar characters: A list of characters attached to this profile
    :vartype characters: List[ourdestiny.d2character]
    :ivar current_season: A season object of the current season in the game
    :vartype current_season: ourdestiny.d2season
    """
    def __init__(self, client_object, profile_json):
        self.client_object = client_object
        self.display_name = profile_json["profile"]["data"]["userInfo"]["displayName"]
        self.membership_type = profile_json["profile"]["data"]["userInfo"]["membershipType"]
        self.membership_id = profile_json["profile"]["data"]["userInfo"]["membershipId"]
        world_cursor = self.client_object.get_world_db_cursor()
        self.current_season = ourdestiny.d2season(self.client_object.get_hash_with_cursor(profile_json["profile"]["data"]["currentSeasonHash"], world_cursor, "Season"), client_object)
        characters_json = self.client_object.get_component_json(self.membership_type,self.membership_id, ["Characters", "CharacterInventories", "CharacterEquipment", "CharacterProgressions"])["Response"]
        self.characters = self.get_character_objects(characters_json)

    def get_character_objects(self, characters_json):

        char_info_json = characters_json["characters"]["data"]
        try:
            char_inv_json = characters_json["characterInventories"]["data"]
        # If we haven't got any inventory items (likely in the case where we're looking at someone else's character), make an empty dummy dictionary
        except KeyError:
            char_inv_json = {}
            for char_id in char_info_json.keys():
                char_inv_json[char_id] = {"items": []}
        char_equip_json = characters_json["characterEquipment"]["data"]
        char_prog_json = characters_json["characterProgressions"]["data"]
        char_list = []
        for char_id in char_info_json.keys():
            char_list.append(ourdestiny.d2character(self.client_object, char_info_json[char_id],
                                                    char_inv_json[char_id]["items"],
                                                    char_equip_json[char_id]["items"],
                                                    char_prog_json[char_id]))
        return char_list
