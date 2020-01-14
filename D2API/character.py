import requests
from D2API import d2client

class d2character(d2client):

    character_id = ""
    membership_type = ""
    light = ""

    def __init__(self, api_key_in, client_id_in, client_secret_in, character_json):
        super().__init__(api_key_in, client_id_in, client_secret_in)
        self.character_id = character_json["characterId"]
        self.membership_type = character_json["membershipType"]
        self.light = character_json["light"]