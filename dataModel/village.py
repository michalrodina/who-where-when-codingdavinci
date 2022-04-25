class village:
    def __init__(self, data):
        self.villageName = data.split("--")[0]
        self.shire = data.split("--")[1]
        self.dataName = data