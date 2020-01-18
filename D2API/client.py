import requests
import json
import secrets
import urllib.parse as urlparse
import sqlite3
import D2API


class d2client:
    api_key = ""
    client_id = ""
    client_secret = ""
    auth_code = ""
    access_token = ""
    refresh_token = ""
    root_endpoint = "https://www.bungie.net/Platform"
    request_header = {}
    bungie_membership_id = ""
    destiny_membership_id = ""
    asset_database = ""
    gear_database = ""
    world_database = ""
    clan_banner_database = ""

    def __init__(self, api_key_in, client_id_in, client_secret_in):
        self.api_key = api_key_in
        self.client_id = client_id_in
        self.client_secret = client_secret_in
        self.TestAccessToken()
        self.ConnectAllDestinyDB()

    def Database(self):
        return D2API.d2database(self.api_key, self.client_id, self.client_secret)

    def GetCharacterObject(self, platform, char_num):
        all_json = self.GetMyCharacters(self.GetMembershipTypeEnum(platform))["Response"]
        char_info_json = all_json["characters"]["data"]
        char_inv_json = all_json["characterInventories"]["data"]
        char_equip_json = all_json["characterEquipment"]["data"]
        count = 0
        for char_id in char_info_json.keys():
            if count == char_num:
                char_info_json = char_info_json[char_id]
                char_inv_json = char_inv_json[char_id]["items"]
                char_equip_json = char_equip_json[char_id]["items"]
            count += 1
        return D2API.d2character(self, char_info_json, char_inv_json, char_equip_json)

    def GetAuthCodeURL(self):
        url = "https://www.bungie.net/en/OAuth/Authorize"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": secrets.token_urlsafe(32)
        }
        auth_request = requests.get(url, params)
        return auth_request.url

    def GetAuthCodeFromURL(self, auth_request_url):
        auth_code_url = input(
            "Please click on this link, and then paste back in the URL you get:\n" + auth_request_url + "\n").strip()
        parser = urlparse.urlparse(auth_code_url)
        self.auth_code = parser.query.split("&")[0].replace("code=", "").strip()

    def GetAuthCode(self):
        self.GetAuthCodeFromURL(self.GetAuthCodeURL())

    def GetAccessToken(self):
        url = "https://www.bungie.net/platform/app/oauth/token/"
        form = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        token_request = requests.post(url, data=form)
        self.StoreAccessToken(token_request.json())

    def RefreshAccessToken(self):
        url = "https://www.bungie.net/platform/app/oauth/token/"
        form = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        token_request = requests.post(url, data=form)
        print(token_request.json())
        self.StoreAccessToken(token_request.json())

    def StoreAccessToken(self, token_request_json):
        self.access_token = token_request_json["access_token"]
        self.refresh_token = token_request_json["refresh_token"]
        self.request_header = {"Authorization": "Bearer " + self.access_token,
                               "X-API-Key": self.api_key}
        with open("./token.json", "w") as jsonfile:
            jsonfile.write(json.dumps(token_request_json))

    def Authenticate(self):
        self.GetAuthCode()
        self.GetAccessToken()

    def TestAccessToken(self):
        try:
            # Tests to see if a token has already been saved
            with open("token.json") as jsonfile:
                token_file_json = json.loads(jsonfile.read())
                self.access_token = token_file_json["access_token"]
                self.refresh_token = token_file_json["refresh_token"]
                self.request_header = {
                    "X-API-Key": self.api_key,
                    "Authorization": self.access_token
                }
                self.bungie_membership_id = token_file_json["membership_id"]
                test_code = self.GetDestinyManifest(testing=True)
                if test_code != 200:
                    # If the file is fine and we've gotten this far, it's likely that the access code has expired and needs refreshing
                    self.RefreshAccessToken()
        except FileNotFoundError:
            # If no token is already saved, get a new one
            self.Authenticate()
        except json.JSONDecodeError:
            # If for some reason there is an error with the JSON file, refresh the file
            self.Authenticate()

    def GetDestinyManifest(self, testing=False):
        url = self.root_endpoint + "/Destiny2/Manifest"
        api_request = requests.get(url, headers=self.request_header)
        if testing == False:
            return api_request.json()
        else:
            return api_request.status_code

    def ConnectAllDestinyDB(self):
        common_path = "./db/"
        with open(common_path + "dbinfo.json") as dbinfo_file:
            dbinfo = json.loads(dbinfo_file.read())

        dbconnect = sqlite3.connect(common_path + dbinfo["mobileAssetContent"])
        self.asset_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileGearAssetDataBase"])
        self.gear_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileWorldContent"])
        self.world_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileClanBannerDatabase"])
        self.clan_banner_database = dbconnect.cursor()

    def GetMembershipTypeEnum(self, platform):
        platform = str(platform)
        if not str.isnumeric(platform):
            if platform == "Xbox" or platform == "XBL":
                return "1"
            elif platform == "PSN" or platform == "Playstation":
                return "2"
            elif platform == "Steam":
                return "3"
            elif platform == "Blizzard":
                return "4"
            elif platform == "Stadia":
                return "5"
            else:
                return "-1"
        else:
            return platform

    def GetFromDB(self, hashnum, table, database="mobileWorldContent"):
        result_json = ""
        # Converts the hash from a JSON file to a column value for the SQL database
        hashnum = int(hashnum)
        if (hashnum & (1 << (32 - 1))) != 0:
            hashnum = hashnum - (1 << 32)
        table = "Destiny"+table+"Definition"
        if database == "mobileWorldContent":
            result_text = \
            self.world_database.execute("SELECT json FROM " + table + " WHERE id = " + str(hashnum)).fetchone()[0]
            result_json = json.loads(result_text)
        elif database == "mobileGearAssetDataBase":
            result_text = \
            self.gear_database.execute("SELECT json FROM " + table + " WHERE id = " + str(hashnum)).fetchone()[0]
            result_json = json.loads(result_text)
        elif database == "mobileAssetContent":
            result_text = \
            self.asset_database.execute("SELECT json FROM " + table + " WHERE id = " + str(hashnum)).fetchone()[0]
            result_json = json.loads(result_text)
        elif database == "mobileClanBannerDatabase":
            result_text = \
            self.clan_banner_database.execute("SELECT json FROM " + table + " WHERE id = " + str(hashnum)).fetchone()[0]
            result_json = json.loads(result_text)
        return result_json

    def GetMyBungieNetUser(self):
        search_request = requests.get(self.root_endpoint + "/User/GetBungieNetUserById/" + self.bungie_membership_id,
                                      headers=self.request_header)
        return search_request.json()

    def GetMyDestinyId(self, platform):
        platform = self.GetMembershipTypeEnum(platform)
        search_request = requests.get(
            self.root_endpoint + "/User/GetMembershipsById/" + self.bungie_membership_id + "/" + platform,
            headers=self.request_header)
        for membership in search_request.json()["Response"]["destinyMemberships"]:
            if str(membership["membershipType"]) == platform:
                self.destiny_membership_id = membership["membershipId"]

    def SearchDestinyPlayer(self, displayname, platform):
        platform = self.GetMembershipTypeEnum(platform)
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/SearchDestinyPlayer/" + platform + "/" + displayname,
            headers=self.request_header)
        return search_request.json()

    def GetMyProfile(self, platform, array_of_enums):
        if self.destiny_membership_id == "":
            self.GetMyDestinyId(platform)
        platform = self.GetMembershipTypeEnum(platform)
        collated_enums = ""
        for enum in array_of_enums:
            collated_enums = collated_enums + enum + ","
        params = {"components": collated_enums}
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/" + platform + "/Profile/" + self.destiny_membership_id,
            headers=self.request_header, params=params)
        return search_request.json()

    def GetMyCharacters(self, platform):
        search_json = self.GetMyProfile(platform, ["Characters", "CharacterInventories", "CharacterEquipment"])
        return search_json

    def GetInstancedItem(self, platform, instance_id):
        platform = self.GetMembershipTypeEnum(platform)
        params = {
            "components": "ItemStats"
        }
        item_request = requests.get(self.root_endpoint+"/Destiny2/"+platform+"/Profile/"+self.destiny_membership_id+"/Item/"+instance_id, params=params, headers=self.request_header)
        return item_request.json()["Response"]
