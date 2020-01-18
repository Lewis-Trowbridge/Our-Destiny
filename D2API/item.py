

class d2item():


    def __init__(self, item_request_json, d2characterobject):
        self.stats = {}
        self.owner_object = d2characterobject
        item_data_json = self.owner_object.client_object.GetFromDB(item_request_json["itemHash"], "InventoryItem")
        self.description = item_data_json["displayProperties"]["description"]
        self.name = item_data_json["displayProperties"]["name"]
        if item_data_json["displayProperties"]["hasIcon"]:
            self.icon_url = item_data_json["displayProperties"]["icon"]
        try:
            self.screenshot_url = item_data_json["screenshot"]
        except KeyError:
            self.screenshot_url = None
        try:
            self.lore = self.owner_object.client_object.GetFromDB(item_data_json["loreHash"], "Lore")["displayProperties"]["description"]
        except KeyError:
            self.lore = None
        try:
            for stat_hash in self.owner_object.client_object.GetFromDB(item_data_json["stats"]["statGroupHash"], "StatGroup")["scaledStats"]:
                self.stats[self.owner_object.client_object.GetFromDB(stat_hash["statHash"], "Stat")["displayProperties"]["name"]] = item_data_json["stats"]["stats"][str(stat_hash["statHash"])]["value"]
        except KeyError:
            self.stats = None



class d2instancedItem(d2item):


    def __init__(self, item_request_json, d2characterobject):
        super().__init__(item_request_json, d2characterobject)
        self.instance_id = item_request_json["itemInstanceId"]
        item_instance_json = self.owner_object.client_object.GetInstancedItem(self.owner_object.membership_type, self.instance_id)
        stat_hashes = item_instance_json["stats"]["data"]["stats"].keys()
        for stat_hash in stat_hashes:
            self.stats[self.owner_object.client_object.GetFromDB(stat_hash, "Stat")["displayProperties"]["name"]] = item_instance_json["stats"]["data"]["stats"][stat_hash]["value"]
