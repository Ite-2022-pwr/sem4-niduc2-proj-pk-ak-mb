import time

import codes
from channels import ChannelModel
from utils.rng import LinearCongruentialGenerator
from typing import Optional


class BinarySymmetricChannel(ChannelModel):

    def __init__(
        self,
        name: str,
        noise_percentage: int,
        seed: int,
        coder_decoder: Optional[codes.CoderDecoder] = None,
    ):
        super().__init__(name, noise_percentage, seed, coder_decoder)

    def transmit(self, message: list[int]) -> list[int]:
        noisy_message = []
        for bit in message:
            random_value = self.rng.next_int_from_range(0, 100)
            if random_value > (100 - self.noise_percentage):
                noisy_message.append(1 if bit == 0 else 0)
            else:
                noisy_message.append(bit)
        return noisy_message

    def transmit_with_coding(self, message: list[int]) -> list[int]:
        if self.coder_decoder is None:
            raise ValueError("CoderDecoder object is required for this method")
        encoded_message = self.coder_decoder.encode(message)
        noisy_message = self.transmit(encoded_message)
        return self.coder_decoder.decode(noisy_message)


if __name__ == "__main__":
    bsc = BinarySymmetricChannel(2, int(time.time()))
    message = []
    n = 1000000
    for i in range(n):
        message.append(bsc.rng.next_int_from_range(0, 1))
    noisy_message = bsc.transmit(message)
    print(sum([1 for i in range(n) if message[i] != noisy_message[i]]) / n * 100)