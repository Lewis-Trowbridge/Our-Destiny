import json
import os
import secrets
import sqlite3
import urllib.parse as urlparse
import zipfile
import requests
import ourdestiny


class d2client:
    """
    The main object that represents your application - automatically authenticates and downloads databases when needed.

    :param api_key_in: The API key gotten from Bungie's website
    :type api_key: string
    :param client_id_in: The client ID gotten from Bungie's website
    :type client_id: string
    :param client_secret_in: The client secret gotten from Bungie's website
    :type client_secret: string
    :cvar api_key: The same API key gotten from Bungie's website, should be the same as during initialisation
    :vartype api_key: string
    :cvar client_id: The same client ID gotten from Bungie's website, should be the same as during initialisation
    :vartype client_id: string
    :cvar client_secret: The same client secret gotten from Bungie's website, should be the same as during initialisation
    :vartype client_secret: string
    :cvar auth_code: The auth code needed to get the access token - if this is already stored, this attribute will be an empty string, as there is no need to go through the full OAuth2 process
    :vartype auth_code: string
    :cvar access_token: The access token needed to authenticate with the API
    :vartype access_token: string
    :cvar refresh_token: The refresh token needed in case the access token expires
    :vartype refresh_token: string
    :cvar root_endpoint: The root endpoint needed to communicate with the API
    :vartype root_endpoint: string
    :cvar request_header: Once authenticated, will allow for any request to be correctly authenticated with the API
    :vartype request_header: dict
    :cvar bungie_membership_id: When retrieved, contains the currently authenticated user's Bungie membership ID, also sometimes called bungienet ID
    :vartype bungie_membership_id: string
    :cvar destiny_membership_id: When obtained, contains the currently authenticated user's Destiny membership ID, needed for most operations to do with the game
    :vartype destiny_membership_id:
    :cvar asset_database: Contains a sqlite3 Cursor object linked to the asset database file - see https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor
    :vartype asset_database: sqlite3.cursor
    :cvar gear_database: Contains a sqlite3 Cursor object linked to the gear database file - see https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor
    :vartype gear_database: sqlite3.cursor
    :cvar world_database: Contains a sqlite3 Cursor object linked to the world database file (the one you'll be using most of the time) - see https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor
    :vartype world_database: sqlite3.cursor
    :cvar clan_banner_database: Contains a sqlite3 Cursor object linked to the clan banner database file - see https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Cursor
    :vartype clan_banner_database: sqlite3.cursor
    """
    api_key = ""
    client_id = ""
    client_secret = ""
    auth_code = ""
    access_token = ""
    refresh_token = ""
    root_endpoint = "https://www.bungie.net/Platform"
    request_header = {}
    #bungie_membership_id = ""
    destiny_membership_id = ""
    asset_database = None
    gear_database = None
    world_database = None
    clan_banner_database = None

    def __init__(self, api_key_in, client_id_in, client_secret_in):
        self.api_key = api_key_in
        self.client_id = client_id_in
        self.client_secret = client_secret_in
        self.test_access_token()
        self.connect_all_destiny_db()

    def get_auth_code_url(self):
        url = "https://www.bungie.net/en/OAuth/Authorize"
        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": state
        }
        auth_request = requests.get(url, params)
        return auth_request.url

    def get_auth_code_from_url(self, auth_request_url):
        auth_code_url = input(
            "Please click on this link, and then paste back in the URL you get:\n" + auth_request_url + "\n").strip()
        parser = urlparse.urlparse(auth_code_url)
        sent_state = urlparse.urlparse(auth_request_url).query.split("state=")[1].split("&")[0]
        returned_state = urlparse.urlparse(auth_code_url).query.split("state=")[1].split("&")[0]
        if sent_state == returned_state:
            self.auth_code = parser.query.split("&")[0].replace("code=", "").strip()
        else:
            raise ourdestiny.StatesDoNotMatch("Remote state does not match current state, aborting")

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

        """
        Called during the initialisation process, tests if the currently stored access token exists and if it is valid.
        """

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

        """
        Gets the Destiny manifest, which contains links to all sqlite and json databases

        :param testing: Variable used in the authentication process to check that an already stored access token is still valid, defaults to False
        :type testing: boolean, optional
        :return: JSON of manifest
        :rtype: dict
        """

        url = self.root_endpoint + "/Destiny2/Manifest"
        api_request = requests.get(url, headers=self.request_header)
        if not testing:
            return api_request.json()
        else:
            return api_request.status_code

    def check_for_destiny_db_update(self):

        """
        Checks through all downloaded databases and checks if there are any updates to any of them - there should be no need to call this, as it should be called automatically during the initialisation process
        """

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

        """
        Unzips a zip file downloaded from bungie.net containing a database file, and adds or updates the corresponding entry in the dbinfo.json file

        :param zipfile_path: The path to the zip file containing the database file
        :type zipfile_path: string
        :param dbtype: The type of database - this can be mobileAssetContent, mobileGearAssetDataBase, mobileWorldContent, or mobileClanBannerDatabase
        :type dbtype: string
        """

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

        """
        Downloads a single database file, unzips it and adds or updates the relevant dbinfo.json entry

        :param dbtype: The type of database - this can be mobileAssetContent, mobileGearAssetDataBase, mobileWorldContent, or mobileClanBannerDatabase
        :type dbtype: string
        :param url: The URL of the database file to download
        :type url: string
        """

        with open("./db/" + dbtype + ".zip", "wb") as db_file:
            db_file.write(requests.get("https://bungie.net" + url).content)
        self.unzip_db_zip("./db/" + dbtype + ".zip", dbtype)

    def download_all_destiny_db(self):

        """
        Downloads all database files, unzips and adds them to the relevant dbinfo.json - normally used automatically in the case of a blank slate
        """

        manifest_json = self.get_destiny_manifest()
        mobile_asset_url = "https://bungie.net" + manifest_json["Response"]["mobileAssetContentPath"]
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

    def connect_all_destiny_db(self):

        """
        Checks if the path to the database files exists, and places the cursor objects for those sqlite databases into the specified class variables
        """

        if os.path.exists("./db"):
            self.check_for_destiny_db_update()
        else:
            os.mkdir("db")
            self.download_all_destiny_db()
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

    def get_world_db_cursor(self):
        common_path = "./db/"
        with open(common_path + "dbinfo.json", "r") as dbinfo_file:
            dbinfo = json.loads(dbinfo_file.read())
        dbconnect = sqlite3.connect(common_path + dbinfo["mobileWorldContent"])
        return dbconnect.cursor()

    def get_hash_with_cursor(self, hashnum, cursor, table):

        hashnum = int(hashnum)
        if (hashnum & (1 << (32 - 1))) != 0:
            hashnum = hashnum - (1 << 32)
        tablename = "Destiny"+table+"Definition"
        db_text = cursor.execute("SELECT json FROM " + tablename + " WHERE id = " + str(hashnum)).fetchone()[0]
        return json.loads(db_text)

    def get_membership_type_enum(self, platform):

        """
        Takes a more generic string of a plaform name and returns the relevant membership type enumerator

        :param platform: The name or enum of the platform the current user is on
        :type platform: string, integer
        :return: The enumerator form of whatever platform name was passed in
        :rtype: string
        """

        platform = str(platform)
        if not str.isnumeric(platform):
            enum_dict = {"Xbox": "1", "XBL": "1", "PSN": "2", "Playstation": "2", "Steam": "3", "Blizzard": "4",
                         "Stadia": "5"}
            try:
                return enum_dict[platform]
            except KeyError:
                return "-1"
        else:
            return platform

    def get_from_db(self, hashnum, table, database="mobileWorldContent"):

        """
        Gets a JSON item from the local sqlite database, using a hash given from the API

        :param hashnum: The hash number given by the API
        :type hashnum: string, integer
        :param table: The table in which to lookup the hash (only the unique part of the table name is needed, for example "lore" instead of "DestinyLoreDefinition")
        :type table: string
        :param database: The database in which to lookup the hash, defaults to world database
        :type database: string, optional
        :return: A JSON of the relevant data
        :rtype: dict
        """

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

        """
        Gets the bungienet object of the currently authenticated user - see https://bungie-net.github.io/multi/operation_get_User-GetBungieNetUserById.html

        :return: A bungienetuser object of the current user's bungienet data - see https://bungie-net.github.io/multi/schema_User-GeneralUser.html
        :rtype: ourdestiny.bungienetuser
        """

        search_request = requests.get(self.root_endpoint + "/User/GetMembershipsForCurrentUser/",
                                      headers=self.request_header)

        return ourdestiny.bungienetuser(search_request.json()["Response"]["bungieNetUser"])

    def get_my_destiny_id(self, platform):
        platform = self.get_membership_type_enum(platform)
        search_request = requests.get(
            self.root_endpoint + "/User/GetMembershipsById/" + self.bungie_membership_id + "/" + platform,
            headers=self.request_header)
        for membership in search_request.json()["Response"]["destinyMemberships"]:
            if str(membership["membershipType"]) == platform:
                self.destiny_membership_id = membership["membershipId"]

    def search_destiny_player(self, displayname, platform):

        """
        Searches and returns the Destiny 2 data of a given display name - see https://bungie-net.github.io/multi/operation_get_Destiny2-SearchDestinyPlayer.html

        :param displayname: The full gamertag or PSN id of the player. Spaces and case are ignored.
        :type displayname: string
        :param platform: The name or enum of the platform the current user is on
        :type platform: string, integer
        :return: A JSON of Destiny user info - see https://bungie-net.github.io/multi/schema_User-UserInfoCard.html
        :rtype: dict
        """

        platform = self.get_membership_type_enum(platform)
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/SearchDestinyPlayer/" + platform + "/" + displayname,
            headers=self.request_header)
        return search_request.json()

    def get_my_profile(self, platform):
        """
        Gets a profile object for the currently authenticated user - see https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html

        :param platform: The name or enum of the platform the current user is on
        :type platform: string, integer
        :return: A d2profile object for the currently authenticated user
        :rtype: ourdestiny.d2profile
        """

        if self.destiny_membership_id == "":
            self.get_my_destiny_id(platform)
        platform = self.get_membership_type_enum(platform)
        params = {"components": "Profiles,ProfileInventories"}
        profile_request = requests.get(
            self.root_endpoint+"/Destiny2/"+platform+"/Profile/"+self.destiny_membership_id,
            headers=self.request_header,
            params=params
        )
        return ourdestiny.d2profile(self, profile_request.json()["Response"])

    def get_bungienetuser_with_membership_id(self, membership_id, platform):

        """
        A method to get a user's bungienetuser object using their membership ID and the platform they are on.

        :param membership_id: The membership ID for the desired user
        :type membership_id: string
        :param platform: The platform the desired user is on
        :type platform: string
        :return: The bungienetuser object for the desired user
        :rtype: ourdestiny.bungienetuser
        """

        platform = self.get_membership_type_enum(platform)
        profile_request = requests.get(self.root_endpoint+"/User/GetMembershipsById/"+membership_id+"/"+platform, headers=self.request_header)
        return ourdestiny.bungienetuser(profile_request.json()["Response"]["bungieNetUser"])

    def get_bunginetusers_with_search_name(self, search_string):
        """
        Gets a list of bungienetusers based on a search string inputted

        :param search_string: String to search for in usernames
        :type search_string: string
        :return: A list of bunginetuser objects based on the search string
        :rtype: List[ourdestiny.bungienetuser]
        """
        params = {"q": search_string}
        search_request = requests.get(self.root_endpoint+"/User/SearchUsers", headers=self.request_header, params=params)#
        users = []
        for user_json in search_request.json()["Response"]:
            users.append(ourdestiny.bungienetuser(user_json))
        return users

    def get_profile_with_search_string(self, search_string, platform):
        """
        Gets a d2profile object based on a search string inputted

        :param search_string: String to search for in usernames
        :type search_string: string
        :param platform: The platform the desired profile is on
        :type platform: string
        :return: The d2profile of the desired user
        :rtype: ourdestiny.d2profile
        """

        platform = self.get_membership_type_enum(platform)
        search_request = requests.get(self.root_endpoint+"/Destiny2/SearchDestinyPlayer/"+platform+"/"+search_string,
                                      headers=self.request_header)
        destiny_membership_id = search_request.json()["Response"][0]["membershipId"]
        params = {"components": "Profiles,ProfileInventories"}
        profile_request = requests.get(self.root_endpoint+"/Destiny2/"+platform+"/Profile/"+destiny_membership_id,
                                       headers=self.request_header,
                                       params=params)
        return ourdestiny.d2profile(self, profile_request.json()["Response"])

    def get_component_json(self, platform, destiny_membership_id, array_of_enums):

        """
        Gets game-related profile information of the currently authenticated user - see https://bungie-net.github.io/multi/operation_get_Destiny2-GetProfile.html

        :param platform: The name or enum of the platform the current user is on
        :type platform: string, integer
        :param array_of_enums: An array of enums - see https://bungie-net.github.io/multi/schema_Destiny-DestinyComponentType.html
        :type array_of_enums: array - strings or integers
        :return: Profile data based on enums given - see https://bungie-net.github.io/multi/schema_Destiny-Responses-DestinyProfileResponse.html
        :rtype: dict
        """

        platform = self.get_membership_type_enum(platform)
        collated_enums = ""
        for enum in array_of_enums:
            collated_enums = collated_enums + enum + ","
        params = {"components": collated_enums}
        search_request = requests.get(
            self.root_endpoint + "/Destiny2/" + platform + "/Profile/" + destiny_membership_id,
            headers=self.request_header, params=params)
        return search_request.json()
