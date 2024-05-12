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
        return array([[i for i in message for j in range(0, 3)]])

    def decode_triple(codded_message):
        decodded_message = []
        list = codded_message[0]
        for i in range(0, len(list), 3):
            counter = Counter()
            for j in range(0, 3):
                counter[list[i + j]] += 1

            value, times = zip(*counter.most_common())
            decodded_message.append(value[0])
            counter.clear()
        return decodded_message

if __name__ == "__main__":
    def __str__(self) -> str:
        return "TripleCoderDekoder"

    def __repr__(self) -> str:
        return "TripleCoderDekoder"

