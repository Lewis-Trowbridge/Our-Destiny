import requests
import D2API


class d2character():
    client_object = ""
    character_id = ""
    membership_type = ""
    light = 0
    mobility = 0
    resilience = 0
    recovery = 0
    discipline = 0
    intellect = 0
    strength = 0
    race = ""
    gender = ""
    cclass = ""
    inventory = []
    equipped = []

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
        #self.inventory = character_inventory_json
        self.equipped = character_equipped_json

    def TestMe(self):
        print(self.client_object.access_token)
    def TestItem(self):
        return D2API.d2item(self.equipped[0], self)