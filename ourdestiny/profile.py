import ourdestiny
import requests

class d2profile:

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
    :ivar membership_type: The membership type enumerator used to represent the platform this profile is registered on
    :vartype membership_type: integer
    :ivar membership_id: The membership ID for this profile
    :vartype membership_id: string
    :ivar characters: A list of characters attached to this profile
    :vartype characters: List[ourdestiny.d2character]
    :ivar vault: The items in the profile's vault
    :vartype vault: List[ourdestiny.d2item]
    :ivar profile_inventory: The profile-level inventory containing items such as planetary currencies and mods
    :vartype profile_inventory: List[ourdestiny.d2item]
    :ivar seasons: The seasons this character owns
    :vartype seasons: List[ourdestiny.d2season]
    :ivar current_season: A season object of the current season in the game
    :vartype current_season: ourdestiny.d2season
    :ivar profile_records: A list of records associated with the current profile
    :vartype profile_records: List[ourdestiny.d2record]
    :ivar record_score: The total triumph score associated with this profile
    :vartype record_score: integer
    """
    def __init__(self, client_object, profile_json):
        self.client_object = client_object
        self.display_name = profile_json["profile"]["data"]["userInfo"]["displayName"]
        self.membership_type = profile_json["profile"]["data"]["userInfo"]["membershipType"]
        self.membership_id = profile_json["profile"]["data"]["userInfo"]["membershipId"]
        world_cursor = self.client_object.get_world_db_cursor()
        self.current_season = ourdestiny.d2season(self.client_object.get_hash_with_cursor(profile_json["profile"]["data"]["currentSeasonHash"], world_cursor, "Season"), self)
        self.seasons = []
        for season_hash in profile_json["profile"]["data"]["seasonHashes"]:
            self.seasons.append(ourdestiny.d2season(self.client_object.get_hash_with_cursor(season_hash, world_cursor, "Season"), self))
        characters_json = self.client_object.get_component_json(self.membership_type, self.membership_id, [ourdestiny.ComponentType.Characters, ourdestiny.ComponentType.CharacterInventories, ourdestiny.ComponentType.CharacterEquipment, ourdestiny.ComponentType.CharacterProgression, ourdestiny.ComponentType.CharacterActivities])["Response"]
        self.characters = self.get_character_objects(characters_json)
        self.profile_inventory = []
        self.vault = []
        self.get_profile_inventories(profile_json["profileInventory"])
        self.profile_records = []
        self.record_score = 0
        self.get_profile_records(profile_json["profileRecords"]["data"])

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
        char_act_json = characters_json["characterActivities"]["data"]
        char_list = []
        for char_id in char_info_json.keys():
            char_list.append(ourdestiny.d2character(self, char_info_json[char_id],
                                                    char_inv_json[char_id]["items"],
                                                    char_equip_json[char_id]["items"],
                                                    char_prog_json[char_id],
                                                    char_act_json[char_id]))
        return char_list

    def get_profile_inventories(self, profileinventory_json):

        try:
            for item in profileinventory_json["data"]["items"]:
                if item["bucketHash"] == 138197802:
                    self.vault.append(ourdestiny.d2item(item, self))
                else:
                    self.profile_inventory.append(ourdestiny.d2item(item, self))
        except KeyError:
            return

    def get_profile_records(self, profile_triumph_json):
        self.record_score = profile_triumph_json["score"]
        for record_hash in profile_triumph_json["records"].keys():
            self.profile_records.append(ourdestiny.d2record(profile_triumph_json["records"][record_hash], self.client_object.get_from_db(record_hash, "Record"), self))

    def get_instanced_item(self, instance_id):

        """
        Gets an instanced item data

        :param instance_id: The id of the item to get instanced data of
        :type instance_id: string
        :return: Instanced data about the item - see https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyItemResponse.html
        :rtype: dict
        """

        params = {
            "components": "ItemInstances,ItemStats,ItemPerks"
        }
        item_request = requests.get(
            self.client_object.root_endpoint + "/Destiny2/" + str(self.membership_type) + "/Profile/" + self.membership_id +
            "/Item/" + instance_id,
            params=params, headers=self.client_object.request_header)
        return item_request.json()["Response"]