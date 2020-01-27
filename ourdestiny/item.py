

class d2item():

    def __init__(self, item_request_json, d2characterobject):
        self.is_equipped = False
        self.can_equip = False
        self.is_instanced_item = False
        self.stats = []
        self.perks = []
        self.attack = None
        self.owner_object = d2characterobject
        item_data_json = self.owner_object.client_object.get_from_db(item_request_json["itemHash"], "InventoryItem")
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
            self.lore = self.owner_object.client_object.get_from_db(item_data_json["loreHash"], "Lore")["displayProperties"]["description"]
        except KeyError:
            self.lore = None
        try:
            self.instance_id = item_request_json["itemInstanceId"]
        except KeyError:
            self.instance_id = None
        try:
            for stat_hash in self.owner_object.client_object.get_from_db(item_data_json["stats"]["statGroupHash"], "StatGroup")["scaledStats"]:
                self.stats.append({"name": self.owner_object.client_object.get_from_db(stat_hash["statHash"], "Stat")["displayProperties"]["name"], "value": item_data_json["stats"]["stats"][str(stat_hash["statHash"])]["value"]})
        except KeyError:
            self.stats = None

    def become_instanced(self):
        if self.instance_id is not None:
            item_instance_json = self.owner_object.client_object.get_instanced_item(self.owner_object.membership_type, self.instance_id)
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
                    self.stats.append({"name": self.owner_object.client_object.get_from_db(stat_hash, "Stat")["displayProperties"]["name"], "value": item_instance_json["stats"]["data"]["stats"][stat_hash]["value"]})
            except KeyError:
                self.stats = []
            self.is_instanced_item = True
            try:
                for perk in item_instance_json["perks"]["data"]["perks"]:
                    perk_json = self.owner_object.client_object.get_from_db(perk["perkHash"], "SandboxPerk")
                    perk_dict = {"name": perk_json["displayProperties"]["name"], "description": perk_json["displayProperties"]["description"], "isActive": perk["isActive"], "isVisible": perk["visible"]}
                    if perk_json["displayProperties"]["hasIcon"]:
                        perk_dict["icon"] = "https://bungie.net" + perk_json["displayProperties"]["icon"]
                    else:
                        perk_dict["icon"] = ""
                    self.perks.append(perk_dict)
            except KeyError:
                pass
        else:
            raise Exception("Item does not have an instance ID")
