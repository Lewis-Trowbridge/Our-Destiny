import requests
from D2API import d2client


class d2character(d2client):
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

    def __init__(self, api_key_in, client_id_in, client_secret_in, character_info_json, character_inventory_json, character_equipped_json):
        super().__init__(api_key_in, client_id_in, client_secret_in)
        self.character_id = character_info_json["characterId"]
        self.membership_type = character_info_json["membershipType"]
        self.light = character_info_json["light"]
        self.mobility = character_info_json["stats"]["2996146975"]
        self.resilience = character_info_json["stats"]["392767087"]
        self.recovery = character_info_json["stats"]["1943323491"]
        self.discipline = character_info_json["stats"]["1735777505"]
        self.intellect = character_info_json["stats"]["144602215"]
        self.strength = character_info_json["stats"]["4244567218"]
        self.race = self.GetFromDB(character_info_json["raceHash"], "Race")["displayProperties"]["name"]
        self.gender = self.GetFromDB(character_info_json["genderHash"], "Gender")["displayProperties"]["name"]
        self.cclass = self.GetFromDB(character_info_json["classHash"], "Class")["displayProperties"]["name"]
        self.inventory = character_inventory_json
        self.equipped = character_equipped_json