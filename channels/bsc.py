import time

import codes
from channels import ChannelModel
from typing import Optional


class BinarySymmetricChannel(ChannelModel):

    def __init__(
        self,
        name: str,
        noise_percentage: int,
        seed: Optional[int] = int(time.time()),
    ):
        super().__init__(name, seed)
        self.noise_percentage = noise_percentage

    def transmit(self, message: list[int]) -> list[int]:
        noisy_message = []
        for bit in message:
            random_value = self.rng.next_int_from_range(0, 100)
            if random_value > (100 - self.noise_percentage):
                noisy_message.append(1 if bit == 0 else 0)
            else:
                noisy_message.append(bit)
        return noisy_message


if __name__ == "__main__":
    bsc = BinarySymmetricChannel("BSC", 2, seed=int(time.time()))
    message = []
    n = 1000000
    for i in range(n):
        message.append(bsc.rng.next_int_from_range(0, 1))
    noisy_message = bsc.transmit(message)
    print(sum([1 for i in range(n) if message[i] != noisy_message[i]]) / n * 100)
