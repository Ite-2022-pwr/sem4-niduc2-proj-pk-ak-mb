from channels import ChannelModel
from typing import Optional

import time
import codes


class GilbertElliotModel(ChannelModel):
    def __init__(
        self,
        name: str,
        error_percentage: int,
        error_repetition_percentage: int,
        seed: Optional[int] = int(time.time()),
        coder_decoder: Optional["codes.CoderDecoder"] = None,
    ):
        super().__init__(name, seed, coder_decoder)
        self.error_percentage = error_percentage
        self.error_repetition_percentage = error_repetition_percentage
        self.state = 0

    def transmit(self, message: list[int]) -> list[int]:
        noisy_message = []
        good_error_change = 0
        error_good_change = 0
        good_repetition = 0
        error_repetition = 0
        for bit in message:
            random_value = self.rng.next_int_from_range(0, 100)
            if self.state == 0:
                if random_value > (100 - self.error_percentage):
                    self.state = 1
                    good_error_change += 1
                    noisy_message.append(1 if bit == 0 else 0)
                else:
                    good_repetition += 1
                    noisy_message.append(bit)
            else:
                if random_value > (100 - self.error_repetition_percentage):
                    error_repetition += 1
                    noisy_message.append(1 if bit == 0 else 0)
                else:
                    self.state = 0
                    error_good_change += 1
                    noisy_message.append(bit)
        print(f"good_error_change: {good_error_change}")
        print(
            f"good_error_change in percentage: {good_error_change / (good_repetition + good_error_change) * 100}%\n"
        )
        print(f"error_good_change: {error_good_change}")
        print(
            f"error_good_change in percentage: {error_good_change / (error_repetition + error_good_change) * 100}%\n"
        )
        print(f"good_repetition: {good_repetition}")
        print(
            f"good_repetition in percentage: {good_repetition / (good_repetition + good_error_change) * 100}%\n"
        )
        print(f"error_repetition: {error_repetition}")
        print(
            f"error_repetition in percentage: {error_repetition / (error_repetition + error_good_change) * 100}%\n"
        )
        return noisy_message

    def transmit_with_coding(self, message: list[int]) -> list[int]:
        if self.coder_decoder is None:
            raise ValueError("CoderDecoder object is required for this method")
        encoded_message = self.coder_decoder.encode(message)
        noisy_message = self.transmit(encoded_message)
        return self.coder_decoder.decode(noisy_message)


if __name__ == "__main__":
    gem = GilbertElliotModel("GEM", 2, 10, seed=int(time.time()))
    message = []
    n = 1000000
    for i in range(n):
        message.append(gem.rng.next_int_from_range(0, 1))
    noisy_message = gem.transmit(message)
    print(
        f"Overall flipped bits percentage: {sum([1 for i in range(n) if message[i] != noisy_message[i]]) / n * 100}%"
    )
