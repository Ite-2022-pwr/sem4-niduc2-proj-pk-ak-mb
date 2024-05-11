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
        self.message = message

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
