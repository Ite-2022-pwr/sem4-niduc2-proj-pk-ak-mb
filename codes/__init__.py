class CoderDecoder:
    def __init__(self, name: str):
        self.name = name

    def encode(self, text):
        raise NotImplementedError("Method not implemented")

    def decode(self, text):
        raise NotImplementedError("Method not implemented")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
