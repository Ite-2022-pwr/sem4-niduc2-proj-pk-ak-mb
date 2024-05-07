

class CoderDecoder:
    def __init__(self, code):
        self.code = code

    def encode(self, text):
        return self.code.encode(text)

    def decode(self, text):
        return self.code.decode(text)