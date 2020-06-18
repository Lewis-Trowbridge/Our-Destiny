import ourdestiny

class d2record:

    """
    A class used to represent a record (or as they are normally known in game, Triumph).

    :param record_request_json: The JSON obtained from the API containing live data, including completion states
    :type record_request_json: dict
    :param record_data_json: The JSON obtained from the database containing generic data
    :type record_data_json: dict
    :param profile_object: The profile object that owns this record
    :type profile_object: ourdestiny.d2profile

    :ivar name: The name of the record
    :vartype name: string
    :ivar description: The description of the record
    :vartype description: string
    :ivar icon: The URL of the icon for the record, if it has one
    :vartype icon: string
    :ivar hash: The hash of the record
    :vartype hash: integer
    :ivar state: The current state(s) of the record
    :vartype state: ourdestiny.d2recordstate
    :ivar reward_items: The items rewarded when completing this triumph, if there are any
    :vartype reward_items: list[ourdestiny.d2item]
    """

    def __init__(self, record_request_json, record_data_json, profile_object):
        self.owner_object = profile_object
        self.name = record_data_json["displayProperties"]["name"]
        self.description = record_data_json["displayProperties"]["description"]
        if record_data_json["displayProperties"]["hasIcon"]:
            self.icon = "https://bungie.net" + record_data_json["displayProperties"]["icon"]
        self.hash = record_data_json["hash"]
        self.state = d2recordstate(record_request_json["state"])
        self.reward_items = []
        try:
            for item in record_data_json["rewardItems"]:
                self.reward_items.append(ourdestiny.d2item(item, profile_object))
        except KeyError:
            pass


class d2recordstate:

    """
    A class representing the current states of a record - see https://bungie-net.github.io/multi/schema_Destiny-DestinyRecordState.html for more explanation

    :param state_num: The number obtained from the API which is used to determine states
    :type state_num: integer

    :ivar none: Indicates the record is in a state where it *could* be redeemed, but it has not been yet.
    :vartype none: bool
    :ivar record_redeemed: Indicates the completed record has been redeemed.
    :vartype record_redeemed: bool
    :ivar record_unavailable: Indicates there's a reward available from this Record but it's unavailable for redemption.
    :vartype record_unavailable: bool
    :ivar objective_not_completed: Indicates the objective for this Record has not yet been completed.
    :vartype objective_not_completed: bool
    :ivar obscured: Indicates that the game recommends that you replace the display text of this Record with DestinyRecordDefinition.stateInfo.obscuredString.
    :vartype obscured: bool
    :ivar invisible: Indicates that the game recommends that you not show this record. Do what you will with this recommendation
    :vartype invisible: bool
    :ivar entitlement_unowned: Indicates that you can't complete this record because you lack some permission that's required to complete it.
    :vartype entitlement_unowned: bool
    :ivar can_equip_title: Indicates the record has a title and you can equip it.
    :vartype can_equip_title: bool
    """

    def __init__(self, state_num):
        self.none = bool(state_num == 0)
        self.record_redeemed = bool(state_num & 1)
        self.record_unavailable = bool(state_num & 2)
        self.objective_not_completed = bool(state_num & 4)
        self.obscured = bool(state_num & 8)
        self.invisible = bool(state_num & 16)
        self.entitlement_unowned = bool(state_num & 32)
        self.can_equip_title = bool(state_num & 64)