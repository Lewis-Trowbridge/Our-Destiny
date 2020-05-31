
class d2item():

    """
    The object form of an in-game item. This can be anything that can be equipped or put in your inventory - guns, armour, sparrows, subclasses, even bounties and quests.

    :param item_request_json: The JSON data of the item obtained from the API
    :type item_request_json: dict
    :param profile_object_in: The object was used to create this item
    :type profile_object_in: ourdestiny.d2profile
    :param character_object_in: The object of the character that owns this item if it has an owner
    :type character_object_in: ourdestiny.d2character

    :ivar description: The description of the item
    :vartype description: string
    :ivar name: The name of the item
    :vartype name: string
    :ivar attack: The value for the main stat of the item - normally attack
    :vartype attack: integer
    :ivar type: The type of the item (hand cannon, auto rifle, rocket launcher...)
    :vartype type: string
    :ivar tier: The tier of the item (Legendary, Rare, Common...)
    :vartype tier: string
    :ivar quantity: The quantity of the item (normally 1 but can be more in the case of currency items)
    :vartype quantity: integer
    :ivar icon_url: The URL to the icon of the item (if it has one)
    :vartype icon_url: string
    :ivar screenshot_url: The URL of the in-game screenshot of the item normally used for backgrounds to items (if it has one)
    :vartype screenshot_url: string
    :ivar lore: The text in the lore tab of the item (if it has one)
    :vartype lore: string
    :ivar instance_id: The unique ID for this item that tracks its instanced data
    :vartype instance_id: string
    :ivar perks: A list of dicts that contain the name, description, and URL of the icon for each perk, as well as boolean values for whether it is active and visible - empty when not instanced, fills when instanced
    :vartype perks: list
    :ivar is_equipped: A value that denotes whether an item is currently equipped or not - defaults to false when not instanced
    :vartype is_equipped: bool
    :ivar can_equip: A value that denotes whether an item can be equipped - differs from is_equipped in that it takes into account more complex requirements for equipping an item, such as level or exotics equipped
    :vartype can_equip: bool
    :ivar is_instanced_item: A value that denotes whether the current item is in its instanced form - meaning it has unique stats and is capable of being equipped among other things
    :vartype is_instanced_item: bool
    :ivar stats: A list of dicts that contain the names and values of each of the stats for this item - generic when not instanced, updates when instanced
    :vartype stats: list
    :ivar owner_object: The object of the character that owns this object
    :vartype owner_object: ourdestiny.d2character
    :ivar profile_object: The object of the profile that was used to create this object
    :vartype profile_object: ourdestiny.d2profile
    :ivar item_hash: The hash value of this item for the database files
    :vartype item_hash: integer
    :ivar bucket_info: The information about what slot this item should fit in - taken directly from the API
    :vartype bucket_info: dict
    """

    def __init__(self, item_request_json, profile_object_in, character_object_in=None):
        self.is_equipped = False
        self.can_equip = False
        self.is_instanced_item = False
        self.stats = []
        self.perks = []
        self.attack = None
        self.quantity = item_request_json["quantity"]
        self.owner_object = character_object_in
        self.profile_object = profile_object_in
        self.item_hash = item_request_json["itemHash"]
        item_data_json = self.profile_object.client_object.get_from_db(self.item_hash, "InventoryItem")
        try:
            self.bucket_info = self.profile_object.client_object.get_from_db(item_request_json["bucketHash"], "InventoryBucket")
        except KeyError:
            self.bucket_info = None
        self.description = item_data_json["displayProperties"]["description"]
        self.name = item_data_json["displayProperties"]["name"]
        self.type = item_data_json["itemTypeDisplayName"]
        try:
            self.tier = item_data_json["inventory"]["tierTypeName"]
        except KeyError:
            self.tier = None
        if item_data_json["displayProperties"]["hasIcon"]:
            self.icon_url = "https://www.bungie.net" + item_data_json["displayProperties"]["icon"]
        try:
            self.screenshot_url = "https://www.bungie.net" + item_data_json["screenshot"]
        except KeyError:
            self.screenshot_url = None
        try:
            self.lore = self.profile_object.client_object.get_from_db(item_data_json["loreHash"], "Lore")["displayProperties"]["description"]
        except KeyError:
            self.lore = None
        try:
            self.instance_id = item_request_json["itemInstanceId"]
        except KeyError:
            self.instance_id = None
        try:
            for stat_hash in self.profile_object.client_object.get_from_db(item_data_json["stats"]["statGroupHash"], "StatGroup")["scaledStats"]:
                self.stats.append({"name": self.profile_object.client_object.get_from_db(stat_hash["statHash"], "Stat")["displayProperties"]["name"], "value": item_data_json["stats"]["stats"][str(stat_hash["statHash"])]["value"]})
        except KeyError:
            self.stats = None

    def become_instanced(self):

        """
        When called, allows an object to become instanced. This updates its can_equip, is_equipped, is_instanced, attack, stats and perk values.
        """

        if self.instance_id is not None:
            dbcursor = self.profile_object.client_object.get_world_db_cursor()
            item_instance_json = self.profile_object.client_object.get_instanced_item(self.owner_object.membership_type, self.instance_id)
            self.can_equip = item_instance_json["instance"]["data"]["canEquip"]
            self.is_equipped = item_instance_json["instance"]["data"]["isEquipped"]
            try:
                self.attack = item_instance_json["instance"]["data"]["primaryStat"]["value"]
            except KeyError:
                self.attack = None
            try:
                self.stats = []
                stat_hashes = item_instance_json["stats"]["data"]["stats"].keys()
                for stat_hash in stat_hashes:
                    self.stats.append({"name": self.profile_object.client_object.get_hash_with_cursor(stat_hash, dbcursor, "Stat")["displayProperties"]["name"], "value": item_instance_json["stats"]["data"]["stats"][stat_hash]["value"]})

            except KeyError:
                self.stats = []
            self.is_instanced_item = True
            try:
                for perk in item_instance_json["perks"]["data"]["perks"]:
                    perk_json = self.profile_object.client_object.get_hash_with_cursor(perk["perkHash"], dbcursor, "SandboxPerk")
                    perk_dict = {"name": perk_json["displayProperties"]["name"], "description": perk_json["displayProperties"]["description"], "isActive": perk["isActive"], "isVisible": perk["visible"]}
                    if perk_json["displayProperties"]["hasIcon"]:
                        perk_dict["icon"] = "https://www.bungie.net" + perk_json["displayProperties"]["icon"]
                    else:
                        perk_dict["icon"] = ""
                    self.perks.append(perk_dict)
            except KeyError:
                pass
        else:
            raise Exception("Item does not have an instance ID")
