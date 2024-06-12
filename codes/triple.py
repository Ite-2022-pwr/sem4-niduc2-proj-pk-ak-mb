import sys
import os
from typing import Tuple, List

from numpy import array
from collections import Counter

__SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(__SCRIPT_DIR))

from functools import reduce
from codes import CoderDecoder


class TripleCoderDecoder(CoderDecoder):
    def __init__(self):
        super().__init__(name="triple")

    def encode(self, message: list[int]) -> list[int]:
        encoded = []
        for bit in message:
            encoded.extend([bit] * 3)
        return encoded

    def decode(self, coded: list[int]) -> tuple[list[int], int]:
        decoded = []
        error_count = 0
        for i in range(0, len(coded), 3):
            chunk = coded[i : i + 3]
            decoded.append(max(set(chunk), key=chunk.count))
            if chunk[0] != chunk[1] or chunk[0] != chunk[2] or chunk[1] != chunk[2]:
                error_count += 1
        return decoded, error_count

    def __str__(self) -> str:
        return "TripleCoderDecoder"


if __name__ == "__main__":
    message = [1, 0, 1, 0, 0, 1, 1, 1]
    coder_decoder = TripleCoderDecoder()
    encoded = coder_decoder.encode(message)
    decoded = coder_decoder.decode(encoded)
    print(f"Message: {message}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print(f"Message == Decoded: {message == decoded}")
