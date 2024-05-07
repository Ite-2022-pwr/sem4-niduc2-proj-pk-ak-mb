from agents import SimulationAgent


class Receiver(SimulationAgent):
    def __init__(self, name: str):
        super().__init__(name)

    def prepare_to_receive(self):
        self.message = []
        self.fragmented_message_chunks = []

    def receive_whole(self, message: list[int]):
        self.message = message

    def receive_chunk(self, message: list[int]):
        self.fragmented_message_chunks.append(message)

    def decode_message(self):
        return self.coderDecoder.decode(self.message)

    def restore_message_from_chunks(self):
        for chunk in self.fragmented_message_chunks:
            for char in chunk:
                self.message.append(char)

    def restore_message_from_chunks_encoded(self):
        for chunk in self.fragmented_message_chunks:
            temp = self.coderDecoder.decode(chunk)
            for char in temp:
                self.message.append(char)
