class d2profile():

    def __init__(self, profile_json):
        self.display_name = profile_json["profile"]["data"]["userInfo"]["displayName"]
        self.membership_type = profile_json["profile"]["data"]["userInfo"]["membershipType"]
        self.membership_id = profile_json["profile"]["data"]["userInfo"]["membershipId"]
        pass

