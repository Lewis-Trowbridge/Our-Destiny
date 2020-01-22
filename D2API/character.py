import requests
import D2API


class d2character():

    def __init__(self, client_object_in, character_info_json, character_inventory_json, character_equipped_json):
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
        self.race = self.client_object.GetFromDB(character_info_json["raceHash"], "Race")["displayProperties"]["name"]
        self.gender = self.client_object.GetFromDB(character_info_json["genderHash"], "Gender")["displayProperties"]["name"]
        self.cclass = self.client_object.GetFromDB(character_info_json["classHash"], "Class")["displayProperties"]["name"]
        inventory_objects = []
        for item in character_inventory_json:
            inventory_objects.append(D2API.d2item(item, self))
        self.inventory = inventory_objects
        equipped_objects = []
        for item in character_equipped_json:
            equipped_objects.append(D2API.d2item(item, self))
        self.equipped = equipped_objects

    def GetEquippedItemByName(self, item_name):
        for item in self.equipped:
            if item.name == item_name:
                return item

    def GetInventoryItemByName(self, item_name):
        for item in self.inventory:
            if item.name == item_name:
                return item

    def GetInstancedEquippedItemByName(self, item_name):
        item = self.GetEquippedItemByName(item_name)
        item.BecomeInstanced()
        return item

    def GetInstancedInventoryItemByName(self, item_name):
        item = self.GetInventoryItemByName(item_name)
        item.BecomeInstanced()
        return item

    def GetEqippedItemByIndex(self, item_index):
        return self.inventory[item_index]

    def GetInventoryItemByIndex(self, item_index):
        return self.inventory[item_index]

    def EquipItem(self, item_to_equip):
        if item_to_equip.is_instanced_item and item_to_equip.can_equip and item_to_equip.owner_object == self:
            data = {
                    "itemId": item_to_equip.instance_id,
                    "characterId": self.character_id,
                    "membershipType": self.membership_type
            }
            equip_request = requests.post(self.client_object.root_endpoint + "/Destiny2/Actions/Items/EquipItem/", json=data, headers=self.client_object.request_header)
            return equip_request.json()
        else:
            raise Exception("Item cannot be equipped")

    def EquipItems(self, array_of_items_to_equip):
        item_ids = []
        for item_to_equip in array_of_items_to_equip:
            if item_to_equip.is_instanced_item and item_to_equip.can_equip and item_to_equip.owner_object == self:
                item_ids.append(item_to_equip.instance_id)
            else:
                raise Exception(item_to_equip.name + "cannot be equipped")
        data = {
            "itemIds": item_ids,
            "characterId": self.character_id,
            "membershipType": self.membership_type
        }
        equip_request = requests.post(self.client_object.root_endpoint + "/Destiny2/Actions/Items/EquipItems/", json=data, headers=self.client_object.request_header)
        return equip_request.json()