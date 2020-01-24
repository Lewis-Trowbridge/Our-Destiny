import json
import os
import secrets
import sqlite3
import urllib.parse as urlparse
import zipfile
import requests
import ourdestiny


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
        self.test_access_token()
        self.connect_all_destiny_db()

    def get_character_object(self, platform, char_num):
        all_json = self.get_my_characters(self.get_membership_type_enum(platform))["Response"]
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
        return ourdestiny.d2character(self, char_info_json, char_inv_json, char_equip_json)

    def get_auth_code_url(self):
        url = "https://www.bungie.net/en/OAuth/Authorize"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": secrets.token_urlsafe(32)
        }
        auth_request = requests.get(url, params)
        return auth_request.url

    def get_auth_code_from_url(self, auth_request_url):
        auth_code_url = input(
            "Please click on this link, and then paste back in the URL you get:\n" + auth_request_url + "\n").strip()
        parser = urlparse.urlparse(auth_code_url)
        self.auth_code = parser.query.split("&")[0].replace("code=", "").strip()

    def get_auth_code(self):
        self.get_auth_code_from_url(self.get_auth_code_url())

    def get_access_token(self):
        url = "https://www.bungie.net/platform/app/oauth/token/"
        form = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        token_request = requests.post(url, data=form)
        self.store_access_token(token_request.json())

    def refresh_access_token(self):
        url = "https://www.bungie.net/platform/app/oauth/token/"
        form = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        token_request = requests.post(url, data=form)
        print(token_request.json())
        self.store_access_token(token_request.json())

    def store_access_token(self, token_request_json):
        self.access_token = token_request_json["access_token"]
        self.refresh_token = token_request_json["refresh_token"]
        self.request_header = {"Authorization": "Bearer " + self.access_token,
                               "X-API-Key": self.api_key}
        with open("./token.json", "w") as jsonfile:
            jsonfile.write(json.dumps(token_request_json))

    def authenticate(self):
        self.get_auth_code()
        self.get_access_token()

    def test_access_token(self):
        try:
            # Tests to see if a token has already been saved
            with open("token.json") as jsonfile:
                token_file_json = json.loads(jsonfile.read())
                self.access_token = token_file_json["access_token"]
                self.refresh_token = token_file_json["refresh_token"]
                self.request_header = {
                    "X-API-Key": self.api_key,
                    "Authorization": "Bearer " + self.access_token
                }
                self.bungie_membership_id = token_file_json["membership_id"]
                test_code = self.get_destiny_manifest(testing=True)
                if test_code != 200:
                    # If the file is fine and we've gotten this far, it's likely that the access code has expired and needs refreshing
                    self.refresh_access_token()
        except FileNotFoundError:
            # If no token is already saved, get a new one
            self.authenticate()
        except json.JSONDecodeError:
            # If for some reason there is an error with the JSON file, refresh the file
            self.authenticate()

    def get_destiny_manifest(self, testing=False):
        url = self.root_endpoint + "/Destiny2/Manifest"
        api_request = requests.get(url, headers=self.request_header)
        if not testing:
            return api_request.json()
        else:
            return api_request.status_code

    def check_for_destiny_db_update(self):
        manifest_json = self.get_destiny_manifest()["Response"]
        with open("./db/dbinfo.json", "r") as dbinfo_file:
            dbinfo = json.loads(dbinfo_file.read())
        if dbinfo["mobileAssetContent"] != manifest_json["mobileAssetContentPath"].replace(
                "/common/destiny2_content/sqlite/asset/", "").strip():
            os.remove("./db/" + dbinfo["mobileAssetContent"])
            self.download_one_destiny_db("mobileAssetContent", manifest_json["mobileAssetContentPath"])
        if dbinfo["mobileGearAssetDataBase"] != manifest_json["mobileGearAssetDataBases"][2]["path"].replace(
                "/common/destiny2_content/sqlite/asset/", "").strip():
            os.remove("./db/" + dbinfo["mobileGearAssetDataBase"])
            self.download_one_destiny_db("mobileGearAssetDataBase", manifest_json["mobileGearAssetDataBases"][2]["path"])
        if dbinfo["mobileWorldContent"] != manifest_json["mobileWorldContentPaths"]["en"].replace(
                "/common/destiny2_content/sqlite/en/", "").strip():
            os.remove("./db/" + dbinfo["mobileWorldContent"])
            self.download_one_destiny_db("mobileWorldContent", manifest_json["mobileWorldContentPaths"]["en"])
        if dbinfo["mobileClanBannerDatabase"] != manifest_json["mobileClanBannerDatabasePath"].replace(
                "/common/destiny2_content/clanbanner/", "").strip():
            os.remove("./db/" + dbinfo["mobileClanBannerDatabase"])
            self.download_one_destiny_db("mobileClanBannerDatabase", manifest_json["mobileClanBannerDatabasePath"])

    def unzip_db_zip(self, zipfile_path, dbtype):
        with zipfile.ZipFile(zipfile_path) as DBZip:
            DBZip.extractall("./db")
            # Opens the file to read its contents and add to the JSON
            with open("./db/dbinfo.json", "r") as dbinfo_json_file:
                try:
                    dbinfo_json = json.loads(dbinfo_json_file.read())
                except json.JSONDecodeError:
                    dbinfo_json = {}
                dbinfo_json[dbtype] = DBZip.namelist()[0]
            # Reopens the file in write mode as this will overwrite the contents of the file immediately, which we do not want
            with open("./db/dbinfo.json", "w") as dbinfo_json_file:
                dbinfo_json_file.write(json.dumps(dbinfo_json))
        os.remove(zipfile_path)

    def download_one_destiny_db(self, dbtype, url):
        with open("./db/" + dbtype + ".zip", "wb") as db_file:
            db_file.write(requests.get("https://bungie.net" + url).content)
        self.unzip_db_zip("./db/" + dbtype + ".zip", dbtype)

    def download_all_destiny_db(self):
        manifest_json = self.get_destiny_manifest()
        mobile_asset_url = "https://bungie.net" + manifest_json["Response"]["mobileAssetContentPath"]
        if not os.path.exists("./db"):
            os.mkdir("db")
        with open("./db/dbinfo.json", "w") as dbinfo_json:
            dbinfo_json.write("")
        with open("./db/MobileAssetContent.zip", "wb") as mobile_asset_file:
            mobile_asset_file.write(requests.get(mobile_asset_url, headers=self.request_header).content)
        self.unzip_db_zip("./db/MobileAssetContent.zip", "mobileAssetContent")
        mobile_asset_gear_url = "https://bungie.net" + manifest_json["Response"]["mobileGearAssetDataBases"][2][
            "path"]
        with open("./db/MobileGearAssetDatabase.zip", "wb") as mobile_asset_gear_file:
            mobile_asset_gear_file.write(
                requests.get(mobile_asset_gear_url, headers=self.request_header).content)
        self.unzip_db_zip("./db/MobileGearAssetDatabase.zip", "mobileGearAssetDataBase")
        mobile_world_content_url = "https://bungie.net" + manifest_json["Response"]["mobileWorldContentPaths"][
            "en"]
        with open("./db/MobileWorldContentDatabase.zip", "wb") as mobile_world_content_file:
            mobile_world_content_file.write(
                requests.get(mobile_world_content_url, headers=self.request_header).content)
        self.unzip_db_zip("./db/MobileWorldContentDatabase.zip", "mobileWorldContent")
        mobile_clan_banner_path = "https://bungie.net" + manifest_json["Response"][
            "mobileClanBannerDatabasePath"]
        with open("./db/MobileClanBannerDatabase.zip", "wb") as mobile_clan_banner_file:
            mobile_clan_banner_file.write(
                requests.get(mobile_clan_banner_path, headers=self.request_header).content)
        self.unzip_db_zip("./db/MobileClanBannerDatabase.zip", "mobileClanBannerDatabase")
        self.connect_all_destiny_db()

    def connect_all_destiny_db(self):
        self.check_for_destiny_db_update()
        common_path = "./db/"
        with open(common_path + "dbinfo.json", "r") as dbinfo_file:
            dbinfo = json.loads(dbinfo_file.read())

        dbconnect = sqlite3.connect(common_path + dbinfo["mobileAssetContent"])
        self.asset_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileGearAssetDataBase"])
        self.gear_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileWorldContent"])
        self.world_database = dbconnect.cursor()
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileClanBannerDatabase"])
        self.clan_banner_database = dbconnect.cursor()

    def get_membership_type_enum(self, platform):
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

    def get_from_db(self, hashnum, table, database="mobileWorldContent"):
        result_json = ""
        # Converts the hash from a JSON file to a column value for the SQL database
        hashnum = int(hashnum)
        if (hashnum & (1 << (32 - 1))) != 0:
            hashnum = hashnum - (1 << 32)
        table = "Destiny" + table + "Definition"
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
                self.clan_banner_database.execute(
                    "SELECT json FROM " + table + " WHERE id = " + str(hashnum)).fetchone()[0]
            result_json = json.loads(result_text)
        return result_json

    def get_my_bungie_net_user(self):
        search_request = requests.get(self.root_endpoint + "/User/GetBungieNetUserById/" + self.bungie_membership_id,
                                      headers=self.request_header)
        return search_request.json()

    def get_my_destiny_id(self, platform):
        platform = self.get_membership_type_enum(platform)
        search_request = requests.get(
            self.root_endpoint + "/User/GetMembershipsById/" + self.bungie_membership_id + "/" + platform,
            headers=self.request_header)
        for membership in search_request.json()["Response"]["destinyMemberships"]:
            if str(membership["membershipType"]) == platform:
                self.destiny_membership_id = membership["membershipId"]

    def search_destiny_player(self, displayname, platform):
        platform = self.get_membership_type_enum(platform)
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/SearchDestinyPlayer/" + platform + "/" + displayname,
            headers=self.request_header)
        return search_request.json()

    def get_my_profile(self, platform, array_of_enums):
        if self.destiny_membership_id == "":
            self.get_my_destiny_id(platform)
        platform = self.get_membership_type_enum(platform)
        collated_enums = ""
        for enum in array_of_enums:
            collated_enums = collated_enums + enum + ","
        params = {"components": collated_enums}
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/" + platform + "/Profile/" + self.destiny_membership_id,
            headers=self.request_header, params=params)
        return search_request.json()

    def get_my_characters(self, platform):
        search_json = self.get_my_profile(platform, ["Characters", "CharacterInventories", "CharacterEquipment"])
        return search_json

    def get_instanced_item(self, platform, instance_id):
        platform = self.get_membership_type_enum(platform)
        params = {
            "components": "ItemInstances,ItemStats,ItemPerks"
        }
        item_request = requests.get(
            self.root_endpoint + "/Destiny2/" + platform + "/Profile/" + self.destiny_membership_id + "/Item/" + instance_id,
            params=params, headers=self.request_header)
        return item_request.json()["Response"]
