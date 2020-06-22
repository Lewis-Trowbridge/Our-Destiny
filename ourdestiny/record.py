import ourdestiny

class d2record(ourdestiny.d2displayproperties):

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
    :ivar objectives: A list of objectives to complete the record
    :vartype objectives: list[ourdestiny.d2recordobjective]
    """

    def __init__(self, record_request_json, record_data_json, profile_object):
        super().__init__(record_data_json["displayProperties"])
        self.owner_object = profile_object
        self.hash = record_data_json["hash"]
        self.state = d2recordstate(record_request_json["state"])
        self.reward_items = []
        try:
            for item in record_data_json["rewardItems"]:
                self.reward_items.append(ourdestiny.d2item(item, profile_object))
        except KeyError:
            pass
        # Records can have either individual or interval objectives, so look for both
        self.objectives = []
        try:
            for objective_json in record_request_json["objectives"]:
                self.objectives.append(d2recordobjective(objective_json, profile_object.client_object.get_from_db(objective_json["objectiveHash"], "Objective")))
        except KeyError:
            pass
        try:
            for objective_json in record_request_json["intervalObjectives"]:
                self.objectives.append(d2recordobjective(objective_json, profile_object.client_object.get_from_db(objective_json["objectiveHash"], "Objective")))
        except KeyError:
            pass

class d2recordobjective(ourdestiny.d2displayproperties):

    """
    A class used to represent an objective of a record

    :param objective_request_json: The JSON obtained from the API containing live data about state of completion
    :type objective_request_json: dict
    :param objective_data_json: The JSON obtained from the database containing generic definitions of the objective
    :type objective_request_json: dict

    :ivar name: Name of the objective, if it has one
    :vartype name: string
    :ivar description: Description of the objective, if it has one
    :vartype description: string
    :ivar progress_description: Text to describe the progress bar
    :vartype progress_description: string
    :ivar hash: The hash of the objective
    :vartype hash: integer
    :ivar progress: The current progress on this objective
    :vartype progress: integer
    :ivar completion_value: The value that must be reached for the objective to be complete
    :vartype completion_value: integer
    :ivar complete: Displays whether the objective is complete
    :vartype complete: bool
    :ivar visible: Displays whether the objective should be visible
    :vartype visible: bool
    :ivar minimum_visibility_threshold: The lowest value the current progress should be before this objective is displayed
    :vartype minimum_visibility_threshold: integer
    :ivar allow_negative_value: Displays whether a negative value is allowed on this objecitve or not
    :vartype allow_negative_value: bool
    :ivar allow_value_change_when_completed: Displays whether value can change when the objective is completed or not
    :vartype allow_value_change_when_completed: bool
    :ivar allow_overcompletion: Displays whether progress will continue past the point of completion or not
    :vartype allow_overcompletion: bool
    :ivar show_value_on_complete: Displays whether progress should be displayed once the objective is complete
    :vartype show_value_on_complete: bool
    :ivar is_counting_downward: Displays whether the objective counts downwards or not
    :vartype is_counting_downward: bool
    """

    def __init__(self, objective_request_json, objective_data_json):
        super().__init__(objective_data_json["displayProperties"])
        self.progress_description = objective_data_json["progressDescription"]
        self.hash = objective_request_json["objectiveHash"]
        self.progress = objective_request_json["progress"]
        self.completion_value = objective_request_json["completionValue"]
        self.complete = objective_request_json["complete"]
        self.visible = objective_request_json["visible"]
        self.minimum_visibility_threshold = objective_data_json["minimumVisibilityThreshold"]
        self.allow_negative_value = objective_data_json["allowNegativeValue"]
        self.allow_value_change_when_completed = objective_data_json["allowValueChangeWhenCompleted"]
        self.allow_overcompletion = objective_data_json["allowOvercompletion"]
        self.show_value_on_complete = objective_data_json["showValueOnComplete"]
        self.is_counting_downward = objective_data_json["isCountingDownward"]


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
