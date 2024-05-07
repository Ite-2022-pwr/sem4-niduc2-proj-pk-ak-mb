import time
from typing import Optional

from utils.rng import LinearCongruentialGenerator


class ChannelModel:

    def __init__(
        self,
        name: str,
        rng_seed: Optional[int] = int(time.time()),
    ):
        self.name = name
        self.rng = LinearCongruentialGenerator(seed=rng_seed)

    def transmit(self, message: list[int]) -> list[int]:
        raise NotImplementedError("Method not implemented")

    def regenerate_rng(self, seed: int):
        self.rng = LinearCongruentialGenerator(seed=seed)

    def regenerate_rng_with_time(self):
        self.rng = LinearCongruentialGenerator(int(time.time()))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
