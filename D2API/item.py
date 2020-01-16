

class d2item():
    owner_object = ""
    name = ""
    description = ""
    icon_url = ""
    screenshot_url = ""
    lore = ""
    stats = {}

    def __init__(self, item_request_json, d2characterobject):
        self.owner_object = d2characterobject
        item_data_json = self.owner_object.client_object.GetFromDB(item_request_json["itemHash"], "InventoryItem")
        self.description = item_data_json["displayProperties"]["description"]
        self.name = item_data_json["displayProperties"]["name"]
        if item_data_json["displayProperties"]["hasIcon"]:
            self.icon_url = item_data_json["displayProperties"]["icon"]
        try:
            self.screenshot_url = item_data_json["screenshot"]
        except KeyError:
            self.screenshot_url = ""
        try:
            self.lore = self.owner_object.client_object.GetFromDB(item_data_json["loreHash"], "Lore")["displayProperties"]["description"]
        except KeyError:
            self.lore = ""
        try:
            for stat_hash in self.owner_object.client_object.GetFromDB(item_data_json["stats"]["statGroupHash"], "StatGroup")["scaledStats"]:
                self.stats[self.owner_object.client_object.GetFromDB(stat_hash["statHash"], "Stat")["displayProperties"]["name"]] = item_data_json["stats"]["stats"][str(stat_hash["statHash"])]["value"]
        except KeyError:
            pass
        pass

