import sys
import os

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

    def decode(self, codded_message: list[int]) -> list[int]:
        decoded = []
        for i in range(0, len(codded_message), 3):
            chunk = codded_message[i : i + 3]
            decoded.append(max(set(chunk), key=chunk.count))
        return decoded

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
