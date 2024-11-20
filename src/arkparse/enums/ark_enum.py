

class ArkEnumValue:
    enum_name: str
    enum_value: str

    def __init__(self, name: str):
        self.enum_name = name.split('::')[0]
        self.enum_value = name.split('::')[1]

    def __str__(self):
        return f"{self.enum_name}->{self.enum_value}"