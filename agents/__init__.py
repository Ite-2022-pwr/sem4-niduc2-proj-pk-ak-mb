from typing import Optional

import codes


class SimulationAgent:

    def __init__(
        self,
        name: str,
        chunk_size: int = 8,
        coder_decoder: Optional[codes.CoderDecoder] = None,
    ):
        self.name = name
        self.chunk_size = chunk_size
        self.coderDecoder = coder_decoder
        self.message = []
        self.fragmented_message_chunks = []

    def set_message(self, message: list[int]):
        self.message.clear()
        self.message = message

    def clear_message(self):
        self.message.clear()

    def set_coder_decoder(self, coder_decoder: codes.CoderDecoder):
        self.coderDecoder = coder_decoder

    def clear_fragmented_message_chunks(self):
        self.fragmented_message_chunks.clear()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
