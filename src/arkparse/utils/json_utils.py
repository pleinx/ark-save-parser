from json import JSONEncoder

class DefaultJsonEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
