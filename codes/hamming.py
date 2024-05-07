import sys
import os

__SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(__SCRIPT_DIR))

from functools import reduce


from codes import CoderDecoder


class HammingCoderDecoder(CoderDecoder):
    def __init__(self, total_bits: int = 7, data_bits: int = 4) -> None:
        super().__init__(name="hamming")
        self.total_bits: int = total_bits
        self.data_bits: int = data_bits
        self.parity_bits: int = self.total_bits - self.data_bits
        self.parity_bits_positions: list[int] = self.calculate_parity_bits_positions()

    def calculate_parity_bits_positions(self) -> list[int]:
        return [2**i for i in range(self.parity_bits) if 2**i <= self.total_bits]

    def find_error_position(self, chunk: list[int]) -> list[int]:
        return (
            reduce(lambda a, b: a ^ b, [i for i, bit in enumerate(chunk) if bit])
            if sum(chunk) != 0
            else 0
        )

    def encode_chunk(self, chunk: list[int]) -> list[int]:
        encoded_chunk = [0] * (self.total_bits + 1)
        j = 0
        for i in range(1, self.total_bits + 1):
            if i in self.parity_bits_positions:
                continue
            encoded_chunk[i] = chunk[j]
            j += 1

        error_position = self.find_error_position(encoded_chunk)
        if error_position in [0] + self.parity_bits_positions:
            encoded_chunk[error_position] = int(not encoded_chunk[error_position])
        else:
            for parity_bit_position in self.parity_bits_positions:
                if parity_bit_position ^ error_position != error_position:
                    encoded_chunk[parity_bit_position] = int(
                        not encoded_chunk[parity_bit_position]
                    )
        return encoded_chunk

    def decode_chunk(self, chunk: list[int]) -> list[int]:
        error_position = self.find_error_position(chunk)
        chunk[error_position] = int(not chunk[error_position])
        return [
            bit
            for i, bit in enumerate(chunk)
            if i not in [0] + self.parity_bits_positions
        ]

    def encode(self, message: list[int]) -> list[int]:
        return super().encode(message)

    def decode(self, message: list[int]) -> list[int]:
        return super().decode(message)


if __name__ == "__main__":
    import numpy as np

    hcd = HammingCoderDecoder()
    chunks = [list(np.random.randint(0, 2, 4)) for i in range(100)]
    for chunk in chunks:
        try:
            encoded_chunk = hcd.encode_chunk(chunk)
            # print(encoded_chunk)
            decoded_chunk = hcd.decode_chunk(encoded_chunk)
            assert chunk == decoded_chunk, f"wanted: {chunk}, have: {decoded_chunk}"
        except AssertionError as err:
            print(err)
