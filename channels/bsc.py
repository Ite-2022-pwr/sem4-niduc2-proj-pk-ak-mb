import time
from typing import Optional

from channels import ChannelModel


class BinarySymmetricChannel(ChannelModel):

    def __init__(
        self,
        name: str,
        noise_percentage: int,
        verbose: Optional[bool] = False,
        seed: Optional[int] = int(time.time()),
    ):
        super().__init__(name, seed)
        self.noise_percentage = noise_percentage
        self.verbose = verbose
        self.bits_flipped = 0
        self.bits_not_flipped = 0

    def transmit(self, message: list[int]) -> list[int]:
        self.bits_flipped = 0
        self.bits_not_flipped = 0
        noisy_message = []
        for bit in message:
            random_value = self.rng.next_int_from_range(0, 100)
            if random_value > (100 - self.noise_percentage):
                noisy_message.append(1 if bit == 0 else 0)
                self.bits_flipped += 1
            else:
                noisy_message.append(bit)
                self.bits_not_flipped += 1
        if self.verbose:
            self.print_verbose()
        print(f"Message:\t\t {message}")
        print(f"Noisy message:\t {noisy_message}")
        return noisy_message

    def print_verbose(self):
        print(f"\nBinary Symmetric Channel: {self.name}")
        print(f"Bits flipped: {self.bits_flipped}")
        print(f"Bits not flipped: {self.bits_not_flipped}")
        print(
            f"Bits flipped in percentage: {self.bits_flipped / (self.bits_flipped + self.bits_not_flipped) * 100}%"
        )


if __name__ == "__main__":
    bsc = BinarySymmetricChannel("BSC", 2, seed=int(time.time()))
    message = []
    n = 1000000
    for i in range(n):
        message.append(bsc.rng.next_int_from_range(0, 1))
    noisy_message = bsc.transmit(message)
    print(sum([1 for i in range(n) if message[i] != noisy_message[i]]) / n * 100)
