import json
import os
import zipfile

import requests
from D2API import d2client

class d2database(d2client):

    def __init__(self, api_key_in, client_id_in, client_secret_in):
        super().__init__(api_key_in, client_id_in, client_secret_in)

    def UnzipDBZip(self, zipfile_path, dbtype):
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

    def DownloadAllDestinyDB(self):
        manifest_json = self.GetDestinyManifest()
        mobile_asset_url = "https://bungie.net" + manifest_json["Response"]["mobileAssetContentPath"]
        if not os.path.exists("./db"):
            os.mkdir("db")
        with open("./db/dbinfo.json", "w") as dbinfo_json:
            dbinfo_json.write("")
        with open("./db/MobileAssetContent.zip", "wb") as mobile_asset_file:
            mobile_asset_file.write(requests.get(mobile_asset_url, headers=self.request_header).content)
        self.UnzipDBZip("./db/MobileAssetContent.zip", "mobileAssetContent")
        mobile_asset_gear_url = "https://bungie.net" + manifest_json["Response"]["mobileGearAssetDataBases"][2]["path"]
        with open("./db/MobileGearAssetDatabase.zip", "wb") as mobile_asset_gear_file:
            mobile_asset_gear_file.write(requests.get(mobile_asset_gear_url, headers=self.request_header).content)
        self.UnzipDBZip("./db/MobileGearAssetDatabase.zip", "mobileGearAssetDataBase")
        mobile_world_content_url = "https://bungie.net" + manifest_json["Response"]["mobileWorldContentPaths"]["en"]
        with open("./db/MobileWorldContentDatabase.zip", "wb") as mobile_world_content_file:
            mobile_world_content_file.write(requests.get(mobile_world_content_url, headers=self.request_header).content)
        self.UnzipDBZip("./db/MobileWorldContentDatabase.zip", "mobileWorldContent")
        mobile_clan_banner_path = "https://bungie.net" + manifest_json["Response"]["mobileClanBannerDatabasePath"]
        with open("./db/MobileClanBannerDatabase.zip", "wb") as mobile_clan_banner_file:
            mobile_clan_banner_file.write(requests.get(mobile_clan_banner_path, headers=self.request_header).content)
        self.UnzipDBZip("./db/MobileClanBannerDatabase.zip", "mobileClanBannerDatabase")
        self.ConnectAllDestinyDB()