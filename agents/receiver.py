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
        self.fragmented_message_chunks = []
        self.fragmented_message_chunks_encoded = []
        self.chunks_with_error_detected = 0
        self.chunks_without_error_detected = 0
        self.chunks_with_fixed_error = 0
        self.chunks_without_fixed_error = 0
        self.chunks_with_missed_error = 0
        self.chunks_with_error_detected_position = []
        self.chunks_without_error_detected_position = []

    def prepare_to_receive(self) -> None:
        self.message = []
        self.fragmented_message_chunks = []
        self.fragmented_message_chunks_encoded = []
        self.chunks_with_error_detected = 0
        self.chunks_without_error_detected = 0
        self.chunks_with_fixed_error = 0
        self.chunks_without_fixed_error = 0
        self.chunks_with_missed_error = 0
        self.chunks_with_error_detected_position = []
        self.chunks_without_error_detected_position = []

    def receive_whole(self, message: list[int]) -> None:
        self.message = message

    def receive_chunk(self, message: list[int]) -> None:
        self.fragmented_message_chunks.append(message)

    def receive_chunk_encoded(self, message: list[int]) -> None:
        self.fragmented_message_chunks_encoded.append(message)

    def decode_message(self) -> list[int] | int:
        return self.coderDecoder.decode(self.message)

    def restore_message_from_chunks(self) -> None:
        for chunk in self.fragmented_message_chunks:
            for char in chunk:
                self.message.append(char)

    def restore_message_from_chunks_encoded(self) -> None:
        i = 0
        for chunk in self.fragmented_message_chunks_encoded:
            decoded_chunk, error_count = self.coderDecoder.decode(chunk)
            if error_count != 0:
                self.chunks_with_error_detected += 1
                self.chunks_with_error_detected_position.append(i)
            else:
                self.chunks_without_error_detected += 1
                self.chunks_without_error_detected_position.append(i)
            i += 1
            self.fragmented_message_chunks.append(decoded_chunk)
            for char in decoded_chunk:
                self.message.append(char)

    def get_error_in_chunk_count(
        self, expected_chunk: list[int], received_chunk: list[int]
    ) -> int:
        return sum(
            [
                1
                for i in range(len(expected_chunk))
                if expected_chunk[i] != received_chunk[i]
            ]
        )

    def get_missed_error_chunk_count(
        self, expected_chunks_list: list[list[int]]
    ) -> int:
        for chunk_pos in self.chunks_without_error_detected_position:
            if (
                self.get_error_in_chunk_count(
                    expected_chunks_list[chunk_pos],
                    self.fragmented_message_chunks[chunk_pos],
                )
                != 0
            ):
                self.chunks_with_missed_error += 1
        return self.chunks_with_missed_error

    def get_error_chunk_count(
        self, expected_chunks_list: list[list[int]], fixedFlag: bool
    ) -> int:
        if fixedFlag:
            for chunk_pos in self.chunks_with_error_detected_position:
                if (
                    self.get_error_in_chunk_count(
                        expected_chunks_list[chunk_pos],
                        self.fragmented_message_chunks[chunk_pos],
                    )
                    == 0
                ):
                    self.chunks_with_fixed_error += 1
            return self.chunks_with_fixed_error
        else:
            for chunk_pos in self.chunks_with_error_detected_position:
                if (
                    self.get_error_in_chunk_count(
                        expected_chunks_list[chunk_pos],
                        self.fragmented_message_chunks[chunk_pos],
                    )
                    != 0
                ):
                    self.chunks_without_fixed_error += 1
            return self.chunks_without_fixed_error
