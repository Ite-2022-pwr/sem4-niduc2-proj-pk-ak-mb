from typing import Optional

from agents import SimulationAgent
from codes import CoderDecoder


class Receiver(SimulationAgent):
    def __init__(
        self,
        name: str,
        chunk_size: Optional[int] = 8,
        coder_decoder: Optional[CoderDecoder] = None,
    ):
        super().__init__(name, chunk_size, coder_decoder)
        self.errors_found = 0
        self.all_errors = 0
        self.missed_errors = 0
        self.fragmented_message_chunks = []
        self.fragmented_message_chunks_encoded = []
        self.chunks_with_detected_errors_positions = []

    def prepare_to_receive(self):
        self.message = []
        self.fragmented_message_chunks = []
        self.fragmented_message_chunks_encoded = []
        self.chunks_with_detected_errors_positions = []
        self.all_errors = 0
        self.missed_errors = 0
        self.errors_found = 0

    def receive_whole(self, message: list[int]):
        self.message = message

    def receive_chunk(self, message: list[int]):
        print(f"Received chunk: {message}")
        self.fragmented_message_chunks.append(message)

    def receive_chunk_encoded(self, message: list[int]):
        print(f"Received encoded chunk: {message}")
        self.fragmented_message_chunks_encoded.append(message)

    def decode_message(self):
        return self.coderDecoder.decode(self.message)

    def restore_message_from_chunks(self):
        for chunk in self.fragmented_message_chunks:
            for char in chunk:
                self.message.append(char)

    def restore_message_from_chunks_encoded(self):
        i = 0
        for chunk in self.fragmented_message_chunks_encoded:
            print(f"\nChunk to decode: {chunk}")
            temp = self.coderDecoder.decode(chunk)
            print(f"\nDecoded chunk: {temp[0]}")
            print(f"Errors found: {temp[1]}")
            if temp[1] != 0:
                self.chunks_with_detected_errors_positions.append(i)
                self.errors_found += temp[1]
            i += 1
            self.fragmented_message_chunks.append(temp[0])
            for char in temp[0]:
                self.message.append(char)

    def get_all_errors_count(self, expected_message: list[int]) -> int:
        return sum(
            [
                1
                for i in range(len(self.message))
                if self.message[i] != expected_message[i]
            ]
        )

    def get_chunk_error_count(
        self, chunk_to_check_pos: int, expected_chunk: list[int]
    ) -> int:
        return sum(
            [
                1
                for i in range(len(self.fragmented_message_chunks[chunk_to_check_pos]))
                if self.fragmented_message_chunks[chunk_to_check_pos][i]
                != expected_chunk[i]
            ]
        )

    def get_missed_errors_count(
        self, expected_fragmented_message_chunks: list[list[int]]
    ) -> int:
        i = 0
        for chunk in self.fragmented_message_chunks:
            self.missed_errors += self.get_chunk_error_count(
                i, expected_fragmented_message_chunks[i]
            )
            if i in self.chunks_with_detected_errors_positions:
                self.missed_errors = max(0, self.missed_errors - 1)
            i += 1
        return self.missed_errors
