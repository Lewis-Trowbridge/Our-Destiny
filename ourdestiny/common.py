class d2displayproperties:

    """
    A base class used to get display properties commonly given in object database definitions - see
    https://bungie-net.github.io/multi/schema_Destiny-Definitions-Common-DestinyDisplayPropertiesDefinition.html
    """

    def __init__(self, display_properties_json):
        try:
            self.name = display_properties_json["name"]
        except KeyError:
            self.name = ""
        try:
            self.description = display_properties_json["description"]
        except KeyError:
            self.description = ""
        if display_properties_json["hasIcon"]:
            self.icon = "https://bungie.net" + display_properties_json["icon"]
        else:
            self.icon = ""
        self.icon_sequences = []
        try:
            for framedict in display_properties_json["iconSequences"]:
                frames = []
                for frame in framedict["frames"]:
                    frames.append("https://bungie.net" + frame)
                self.icon_sequences.append(frames)
        except KeyError:
            pass
        try:
            self.high_res_icon = "https://bungie.net" + display_properties_json["highResIcon"]
        except KeyError:
            self.high_res_icon = ""