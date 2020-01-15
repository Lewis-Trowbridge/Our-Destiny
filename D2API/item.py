

class d2item():
    name = ""
    description = ""
    icon_url = ""
    screenshot_url = ""

    def __init__(self, item_request_json, d2characterobject):
        item_data_json = d2characterobject.client_object.GetFromDB(item_request_json["itemHash"], "InventoryItem")
        self.description = item_data_json["displayProperties"]["description"]
        self.name = item_data_json["displayProperties"]["name"]
        if item_data_json["displayProperties"]["hasIcon"]:
            self.icon_url = item_data_json["displayProperties"]["icon"]
        try:
            self.screenshot_url = item_data_json["screenshot"]
        except KeyError:
            self.screenshot_url = ""

