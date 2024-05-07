from typing import Optional
from utils.rng import LinearCongruentialGenerator

import codes
import time


class ChannelModel:

    def __init__(
        self,
        name: str,
        noise_percentage: int,
        rng_seed: Optional[int] = int(time.time()),
        coder_decoder: Optional["codes.CoderDecoder"] = None,
    ):
        self.name = name
        self.rng = LinearCongruentialGenerator(seed=rng_seed)
        self.noise_percentage = noise_percentage
        self.coder_decoder = coder_decoder

    def transmit(self, message: list[int]) -> list[int]:
        raise NotImplementedError("Method not implemented")

    def transmit_with_coding(self, message: list[int]) -> list[int]:
        raise NotImplementedError("Method not implemented")

    def regenerate_rng(self, seed: int):
        self.rng = LinearCongruentialGenerator(seed=seed)

    def regenerate_rng_with_time(self):
        self.rng = LinearCongruentialGenerator(int(time.time()))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
