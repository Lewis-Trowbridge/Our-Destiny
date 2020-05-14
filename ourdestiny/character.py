import requests
from concurrent.futures import ThreadPoolExecutor, wait
import ourdestiny


class d2character():

    """
    The object that represents an in-game character, containing attributes and methods related to character information
    and management. Should be produced by the profile's get_character_object method.

    :param client_object_in: The client object that created the character object. Allows the character object to authenticate and lookup items in database files without needing to rewrite methods or produce multiple client objects
    :type client_object_in: ourdestiny.d2client
    :param character_info_json: The JSON containing the basic character data obtained from GetProfile
    :type character_info_json: dict
    :param character_inventory_json: The JSON containing the data for all of the items in the character's inventory obtained from GetProfile
    :type character_inventory_json: dict
    :param character_equipped_json: The JSON containing the data for all of the items equipped to the character obtained from GetProfile
    :type character_equipped_json: dict
    :param character_progression_json: The JSON containing the data for all of the character progressions
    :type character_progression_json: dict
    :ivar client_object: The d2client object that created this character object
    :vartype client_object: ourdestiny.d2client
    :ivar character_id: The character ID for this character
    :vartype character_id: string
    :ivar membership_type: The membership type (platform) enum for the platform this character is on
    :vartype membership_type: integer
    :ivar light: The light (or power as it was formerly known, or light before that, thanks Bungie) level of this character
    :vartype light: integer
    :ivar mobility: The mobility of this character
    :vartype mobility: integer
    :ivar resilience: The resilience of this character
    :vartype resilience: integer
    :ivar recovery: The recovery of this character
    :vartype recovery: integer
    :ivar discipline: The discipline of this character
    :vartype discipline: integer
    :ivar intellect: The intellect of this character
    :vartype intellect: integer
    :ivar strength: The strength of this character
    :vartype strength: integer
    :ivar race: The race of this character (Human, Awoken, or Exo)
    :vartype race: string
    :ivar gender: The gender of this character
    :vartype gender: string
    :ivar cclass: The class of this character - note the extra c, since "class" is a reserved keyword
    :vartype cclass: string
    :ivar inventory: A list of d2item objects in the character's inventory
    :vartype inventory: list
    :ivar equipped: A list of d2item objects currently equipped to the character
    :vartype equipped: list
    :ivar progressions: A list of d2progression objects containing data about progressions on this character - e.g glory ranks, infamy ranks
    :vartype progressions: list
    :ivar factions: A list of d2faction objects containing data about factions
    :vartype factions: list
    """

    def __init__(self, client_object_in, character_info_json, character_inventory_json, character_equipped_json, character_progression_json):
        self.client_object = client_object_in
        self.character_id = character_info_json["characterId"]
        self.membership_type = character_info_json["membershipType"]
        self.light = character_info_json["light"]
        self.mobility = character_info_json["stats"]["2996146975"]
        self.resilience = character_info_json["stats"]["392767087"]
        self.recovery = character_info_json["stats"]["1943323491"]
        self.discipline = character_info_json["stats"]["1735777505"]
        self.intellect = character_info_json["stats"]["144602215"]
        self.strength = character_info_json["stats"]["4244567218"]
        self.race = self.client_object.get_from_db(character_info_json["raceHash"], "Race")["displayProperties"]["name"]
        self.gender = self.client_object.get_from_db(character_info_json["genderHash"], "Gender")["displayProperties"]["name"]
        self.cclass = self.client_object.get_from_db(character_info_json["classHash"], "Class")["displayProperties"]["name"]
        inventory_objects = []
        for item in character_inventory_json:
            inventory_objects.append(ourdestiny.d2item(item, self))
        self.inventory = inventory_objects
        equipped_objects = []
        for item in character_equipped_json:
            equipped_objects.append(ourdestiny.d2item(item, self))
        self.equipped = equipped_objects
        progression_list = []
        for progression_hash in character_progression_json["progressions"].keys():
            progression_db_json = self.client_object.get_from_db(progression_hash, "Progression")
            progression_list.append(ourdestiny.d2progression(progression_db_json))
        self.progressions = progression_list
        faction_list = []
        for faction_hash in character_progression_json["factions"].keys():
            faction_list.append(ourdestiny.d2faction(self.client_object.get_from_db(faction_hash, "Faction"), self))
        self.factions = faction_list

    def get_equipped_item_by_name(self, item_name):

        """
        Gets an item currently equipped to this character

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: ourdestiny.d2item
        """

        for item in self.equipped:
            if item.name == item_name:
                return item

    def get_inventory_item_by_name(self, item_name):

        """
        Gets an item in the character's inventory

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: d2item
        """

        for item in self.inventory:
            if item.name == item_name:
                return item

    def get_item_by_name(self, item_name):

        """
        Gets an item from the character's inventory **and** equipped items

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: ourdestiny.d2item
        """

        item = self.get_equipped_item_by_name(item_name)
        if item is not None:
            return item
        else:
            item = self.get_inventory_item_by_name(item_name)
            return item

    def get_instanced_equipped_item_by_name(self, item_name):

        """
        Gets an instanced item from the character's equipped item

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: ourdestiny.d2item
        """

        item = self.get_equipped_item_by_name(item_name)
        item.become_instanced()
        return item

    def get_instanced_equipped_items_by_name(self, list_of_items_to_get):
        """
        Gets a list of instanced items from the character's equipped items

        :param list_of_items_to_get: A list of strings of items to get
        :type list_of_items_to_get: List[str]
        :return: A list of requested items
        :rtype: List[ourdestiny.d2item]
        """

        items_gotten = []
        futures = []
        pool = ThreadPoolExecutor()
        for item_name in list_of_items_to_get:
            futures.append(pool.submit(self.get_instanced_equipped_item_by_name, item_name))
        wait(futures)
        for future in futures:
            items_gotten.append(future.result())
        pool.shutdown()
        return items_gotten


    def get_instanced_inventory_item_by_name(self, item_name):

        """
        Gets an instanced item from the character's inventory

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: ourdestiny.d2item
        """

        item = self.get_inventory_item_by_name(item_name)
        item.become_instanced()
        return item

    def get_instanced_inventory_items_by_name(self, list_of_items_to_get):

        """
        Gets a list of instanced items from the character's inventory

        :param list_of_items_to_get: A list of strings of items to get
        :type list_of_items_to_get: List[str]
        :return: A list of items that could be found.
        :rtype: List[ourdestiny.d2item]
        """

        items_gotten = []
        futures = []
        pool = ThreadPoolExecutor()
        for item_name in list_of_items_to_get:
            futures.append(pool.submit(self.get_instanced_inventory_item_by_name, item_name))
        wait(futures)
        for future in futures:
            items_gotten.append(future.result())
        pool.shutdown()
        return items_gotten


    def get_instanced_item_by_name(self, item_name):

        """
        Gets an instanced item from the character's inventory or equipped items

        :param item_name: The exact, case-sensitive name of the item you're looking for
        :type item_name: string
        :return: The requested item object
        :rtype: ourdestiny.d2item
        """

        item = self.get_equipped_item_by_name(item_name)
        if item is not None:
            item.become_instanced()
            return item
        else:
            item = self.get_inventory_item_by_name(item_name)
            if item is not None:
                item.become_instanced()
                return item

    def get_instanced_items_by_name(self, array_of_names):

        with ThreadPoolExecutor() as pool:
            for name in array_of_names:
                pool.submit(self.get_instanced_equipped_item_by_name, name)

    def get_equipped_item_by_index(self, item_index):

        """
        Gets an item from the character's equipped items by index

        :param item_index: The 0-based index of the item in the list of the character's equipped items
        :type item_index: integer
        :return: The item object at the index given
        :rtype: ourdestiny.d2item
        """

        return self.equipped[item_index]

    def get_inventory_item_by_index(self, item_index):

        """
        Gets an item from the character's inventory items by index

        :param item_index: The 0-based index of the item in the list of the character's inventory items
        :type item_index: integer
        :return: The item object at the index given
        :rtype: ourdestiny.d2item
        """

        return self.inventory[item_index]

    def get_item_in_slot(self, slot):

        """
        Gets an equipped item in an inventory slot - uses one of two corresponding values for each slot, shown below:

        | Kinetic Weapons: 0
        | Energy Weapons: 1
        | Power Weapons: 2
        | Helmet: 3
        | Gauntlets: 4
        | Chest Armor: 5
        | Leg Armor: 6
        | Class Armor: 7
        | Ghost: 8
        | Vehicle: 9
        | Ships: 10
        | Subclass: 16
        | Clan Banners: 17
        | Emblems: 27
        | Finishers: 47
        | Emotes: 12
        | Seasonal Artifact: 49

        :param slot: The slot being targeted
        :type slot: string or integer
        :return: The equipped item in the slot
        :rtype: ourdestiny.d2item
        """

        for item in self.equipped:
            if item.bucket_info["displayProperties"]["name"] == slot or item.bucket_info["index"] == slot:
                return item

    def get_item_in_same_slot(self, item_to_check):

        """
        Gets the currently equipped item in the same slot as the item passed in

        :param item_to_check: The item to get the equipped item in the same slot as
        :type item_to_check: ourdestiny.d2item
        :return: The item in the same slot as the equipped item
        :rtype: ourdestiny.d2item
        """

        for item in self.equipped:
            if item.bucket_info["index"] == item_to_check.bucket_info["index"]:
                return item

    def equip_item(self, item_to_equip):

        """
        Takes an *instanced* d2item object, and equips it if it is instanced, is equippable, and belongs to the current character

        :param item_to_equip: The object of the item to be equipped to the current character
        :type item_to_equip: ourdestiny.d2item
        :return: The response JSON from the API - see https://bungie-net.github.io/multi/operation_post_Destiny2-EquipItem.html
        :rtype: dict
        """

        item_to_equip.become_instanced()
        if item_to_equip.is_instanced_item and item_to_equip.can_equip and item_to_equip.owner_object == self:
            data = {
                    "itemId": item_to_equip.instance_id,
                    "characterId": self.character_id,
                    "membershipType": self.membership_type
            }
            equip_request = requests.post(self.client_object.root_endpoint + "/Destiny2/Actions/Items/EquipItem/", json=data, headers=self.client_object.request_header)
            item_to_equip.become_instanced()
            return equip_request.json()
        else:
            raise Exception("Item cannot be equipped")

    def equip_items(self, array_of_items_to_equip):

        """
        Takes an array of *instanced* items, and equips them if they are instanced, equippable and belong to the current character

        :param array_of_items_to_equip: A list of item objects to be equipped to the current character
        :type array_of_items_to_equip: List[ourdestiny.d2item]
        :return: The response JSON from the API - see https://bungie-net.github.io/multi/schema_Destiny-DestinyEquipItemResults.html
        :rtype: dict
        """

        item_ids = []
        items_replaced = []
        for item_to_equip in array_of_items_to_equip:
            if item_to_equip.is_instanced_item and item_to_equip.can_equip and item_to_equip.owner_object == self:
                item_ids.append(item_to_equip.instance_id)
                items_replaced.append(self.get_item_in_same_slot(item_to_equip))
            else:
                raise Exception(item_to_equip.name + "cannot be equipped")
        data = {
            "itemIds": item_ids,
            "characterId": self.character_id,
            "membershipType": self.membership_type
        }
        equip_request = requests.post(self.client_object.root_endpoint + "/Destiny2/Actions/Items/EquipItems/", json=data, headers=self.client_object.request_header)
        count = 0
        futures = []
        pool = ThreadPoolExecutor()
        for item_to_equip in array_of_items_to_equip:
            futures.append(pool.submit(item_to_equip.become_instanced))
            futures.append(pool.submit(items_replaced[count].become_instanced))
            self.swap_item(items_replaced[count], array_of_items_to_equip[count])
            count += 1
        wait(futures)
        pool.shutdown()
        return equip_request.json()

    def swap_item(self, item_in_equipped, item_in_inventory):

        """
        **Do not use for equipping items to an in-game character, this is used to keep consistency locally due to Bungie's API not updating its inventories instantly.**

        Swaps a currently equipped item with an inventory item in the local character object

        :param item_in_equipped: Item in equipped list to be swapped
        :type item_in_equipped: ourdestiny.d2item
        :param item_in_inventory: Item in inventory list to be swapped
        :type item_in_inventory: ourdestiny.d2item
        """
        self.equipped[self.equipped.index(item_in_equipped)] = item_in_inventory
        self.inventory[self.inventory.index(item_in_inventory)] = item_in_equipped

    def transfer_item(self, item_to_transfer, number_to_transfer=1):

        """
        Transfers an *instanced* item to or from the vault

        :param item_to_transfer: The item object to be transferred to the vault
        :type item_to_transfer: d2item
        :param number_to_transfer: The number of items to transfer to the vault - defaults to 1, but can be increased in the case of stacks of items, such as planetary materials
        :type number_to_transfer: integer
        :return: The response JSON from the API - see https://bungie-net.github.io/multi/schema_Destiny-DestinyEquipItemResults.html
        :rtype: dict
        """

        if item_to_transfer is not None and item_to_transfer.is_instanced_item and item_to_transfer.owner_object == self:
            item_hash = item_to_transfer.item_hash
            item_id = item_to_transfer.instance_id
            data = {
                "itemReferenceHash": item_hash,
                "stackSize": number_to_transfer,
                "transferToVault": True,
                "itemId": item_id,
                "characterId": self.character_id,
                "membershipType": self.membership_type
            }
            transfer_request = requests.post(self.client_object.root_endpoint + "/Destiny2/Actions/Items/TransferItem", json=data, headers=self.client_object.request_header)
            return transfer_request.json()