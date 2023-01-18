class App:
    def __init__(self, app_json: dict = None):
        if app_json:
            self.fromJSON(app_json)
        else:
            self.title = ""
            self.path = ""
            self.hours = 0
            self.minutes = 0

    def toJSON(self):
        return {
                "title": self.title,
                "path": self.path,
                "total_time": {
                        "hours": self.hours,
                        "minutes": self.minutes
                    }
            }

    def fromJSON(self, app_json: dict):
        self.title = app_json['title']
        self.path = app_json['path']
        self.hours = app_json['total_time']['hours']
        self.minutes = app_json['total_time']['minutes']
