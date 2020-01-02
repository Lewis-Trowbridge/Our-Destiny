import requests
import json
import secrets
import urllib.parse as urlparse
import sqlite3
import zipfile
import os

class D2API:
    api_key = ""
    client_id = ""
    client_secret = ""
    auth_code = ""
    access_token = ""
    refresh_token = ""
    root_endpoint = "https://www.bungie.net/Platform"
    request_header = {}

    def __init__(self, api_key_in, client_id_in, client_secret_in):
        self.api_key = api_key_in
        self.client_id = client_id_in
        self.client_secret = client_secret_in
        self.TestAccessToken()

    def GetAuthCodeURL(self):
        url = "https://www.bungie.net/en/OAuth/Authorize"
        params = {
            "response_type":"code",
            "client_id": self.client_id,
            "state": secrets.token_urlsafe(32)
        }
        auth_request = requests.get(url, params)
        return auth_request.url

    def GetAuthCodeFromURL(self, auth_request_url):
        auth_code_url = input("Please click on this link, and then paste back in the URL you get:\n" + auth_request_url + "\n").strip()
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
        self.request_header = {"Authorization": "Bearer "+self.access_token,
                               "X-API-Key":self.api_key}
        with open("token.json", "w") as jsonfile:
            jsonfile.write(json.dumps(token_request_json))

    def Authenticate(self):
        self.GetAuthCode()
        self.GetAccessToken()

    def TestAccessToken(self):
        try:
            #Tests to see if a token has already been saved
            with open("./token.json") as jsonfile:
                token_file_json = json.loads(jsonfile.read())
                self.access_token = token_file_json["access_token"]
                self.refresh_token = token_file_json["refresh_token"]
                test_code = self.GetDestinyManifest(testing=True)
                if test_code != 200:
                    #If the file is fine and we've gotten this far, it's likely that the access code has expired and needs refreshing
                    self.RefreshAccessToken()
        except FileNotFoundError:
            #If no token is already saved, get a new one
            self.Authenticate()
        except json.JSONDecodeError:
            #If for some reason there is an error with the JSON file, refresh the file
            self.Authenticate()

    def GetDestinyManifest(self, testing=False):
        url = self.root_endpoint+"/Destiny2/Manifest"
        api_request = requests.get(url, headers=self.request_header)
        if testing == False:
            return api_request.json()
        else:
            return api_request.status_code

    def UnzipFile(self, zipfile_path):
        with zipfile.ZipFile(zipfile_path) as DBZip:
            print(DBZip.namelist())
            DBZip.extractall("./db")
        os.remove(zipfile_path)


    def DownloadAllDestinyDB(self):
        manifest_json = self.GetDestinyManifest()
        mobile_asset_url = "https://bungie.net"+manifest_json["Response"]["mobileAssetContentPath"]
        if not os.path.exists("./db"):
            os.mkdir("db")
        with open("./db/MobileAssetContent.zip", "wb") as mobile_asset_file:
            mobile_asset_file.write(requests.get(mobile_asset_url, headers=self.request_header).content)
        self.UnzipFile("./db/MobileAssetContent.zip")
        mobile_asset_gear_url = "https://bungie.net"+manifest_json["Response"]["mobileGearAssetDataBases"][2]["path"]
        with open("./db/MobileGearAssetDatabase.zip", "wb") as mobile_asset_gear_file:
            mobile_asset_gear_file.write(requests.get(mobile_asset_gear_url, headers=self.request_header).content)
        self.UnzipFile("./db/MobileGearAssetDatabase.zip")
        mobile_world_content_url = "https://bungie.net"+manifest_json["Response"]["mobileWorldContentPaths"]["en"]
        with open("./db/MobileWorldContentDatabase.zip", "wb") as mobile_world_content_file:
            mobile_world_content_file.write(requests.get(mobile_world_content_url, headers=self.request_header).content)
        self.UnzipFile("./db/MobileWorldContentDatabase.zip")
