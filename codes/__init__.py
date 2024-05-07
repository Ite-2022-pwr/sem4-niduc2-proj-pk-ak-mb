class CoderDecoder:
    def __init__(self, code):
        self.code = code

    def encode(self, text):
        raise NotImplementedError

    def decode(self, text):
        raise NotImplementedError
