import time
from typing import Optional

from channels import ChannelModel


class GilbertElliotModel(ChannelModel):
    def __init__(
        self,
        name: str,
        error_percentage: int,
        error_repetition_percentage: int,
        verbose: Optional[bool] = False,
        seed: Optional[int] = int(time.time()),
    ):
        super().__init__(name, seed)
        self.error_percentage = error_percentage
        self.error_repetition_percentage = error_repetition_percentage
        self.state = 0  # 0 - good state, 1 - error state
        self.verbose = verbose
        self.good_error_change = 0
        self.error_good_change = 0
        self.good_repetition = 0
        self.error_repetition = 0

    def transmit(self, message: list[int]) -> list[int]:
        noisy_message = []
        self.good_error_change = 0
        self.error_good_change = 0
        self.good_repetition = 0
        self.error_repetition = 0
        for bit in message:
            random_value = self.rng.next_int_from_range(0, 100)
            if self.state == 0:
                if random_value > (100 - self.error_percentage):
                    self.state = 1
                    self.good_error_change += 1
                    noisy_message.append(1 if bit == 0 else 0)
                else:
                    self.good_repetition += 1
                    noisy_message.append(bit)
            else:
                if random_value > (100 - self.error_repetition_percentage):
                    self.error_repetition += 1
                    noisy_message.append(1 if bit == 0 else 0)
                else:
                    self.state = 0
                    self.error_good_change += 1
                    noisy_message.append(bit)
        self.print_verbose()
        return noisy_message

    def print_verbose(self):
        print(f"Good to error state changes: {self.good_error_change}")
        print(f"Error to good state changes: {self.error_good_change}")
        print(f"Good state repetitions: {self.good_repetition}")
        print(f"Error state repetitions: {self.error_repetition}")
        print(f"good_error_change: {self.good_error_change}")
        try:
            print(
                f"good_error_change in percentage: {self.good_error_change / (self.good_repetition + self.good_error_change) * 100}%\n"
            )
        except ZeroDivisionError:
            print("self.good_error_change in percentage: 0%\n")
        print(f"error_good_change: {self.error_good_change}")
        try:
            print(
                f"error_good_change in percentage: {self.error_good_change / (self.error_repetition + self.error_good_change) * 100}%\n"
            )
        except ZeroDivisionError:
            print("self.error_good_change in percentage: 0%\n")
        print(f"good_repetition: {self.good_repetition}")
        try:
            print(
                f"good_repetition in percentage: {self.good_repetition / (self.good_repetition + self.good_error_change) * 100}%\n"
            )
        except ZeroDivisionError:
            print("self.good_repetition in percentage: 0%\n")
        print(f"error_repetition: {self.error_repetition}")
        try:
            print(
                f"error_repetition in percentage: {self.error_repetition / (self.error_repetition + self.error_good_change) * 100}%\n"
            )
        except ZeroDivisionError:
            print("self.error_repetition in percentage: 0%\n")


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
