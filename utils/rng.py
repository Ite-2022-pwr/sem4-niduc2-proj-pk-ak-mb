import os
import time
import math

from typing import Generator


class LinearCongruentialGenerator:
    """Pseudorandom number generator"""

    def __init__(
        self, a: int = 48271, c: int = 0, m: int = 2**31 - 1, seed: int = None
    ):
        """LCG constructor
        :param: a - the multiplier
        :param: c - the increment
        :param: m - the modulus
        :param: seed - the start value
        """

        assert 0 < m, "param m (modulus) must be a positive number"
        assert 0 < a < m, "param a (multiplier) must be 0 < a < m"
        assert 0 <= c < m, "param c (increment) must be 0 <= c < m"

        self.__multiplier = a
        self.__increment = c
        self.__modulus = m

        if seed is None:
            self.__x0 = int(os.getpid() + time.time())
        else:
            assert 0 <= seed < m, "param seed must be 0 <= seed < m"
            self.__x0 = seed

        self.__x_next = (
            self.__multiplier * self.__x0 + self.__increment
        ) % self.__modulus

    def next_int(self) -> int:
        """Generates pseudorandom integer"""
        self.__x_next = (
            self.__multiplier * self.__x_next + self.__increment
        ) % self.__modulus
        return self.__x_next

    def next_float(self) -> float:
        """Generates pseudorandom float"""
        return self.next_int() / self.__modulus

    def next_int_from_range(self, low: int, high: int) -> int:
        """Genereates pseudorandom integer from given range [low; high]"""
        if low > high:
            raise ValueError("param high must be greater than param low")
        return self.next_int() % (high - low + 1) + low

    def next_float_from_range(self, low: float, high: float) -> float:
        """Genereate pseudorandom float from given range [low; high]"""
        if low > high:
            raise ValueError("param high must be greater than param low")
        return self.next_float() * (high - low) + low

    def generate_ints(
        self, n: int, genrange: tuple[int, int] = None
    ) -> Generator[int, None, None]:
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"param n must be positive int, given: {n} ({type(n)})")

        if genrange is None:
            return (self.next_int() for _ in range(n))
        else:
            if not isinstance(genrange, tuple) and len(genrange) != 2:
                raise ValueError("param range must be a tuple (low, high) or None")
            if genrange[0] > genrange[1]:
                raise ValueError(
                    "in param genrange second number should be greater than first"
                )
            return (
                self.next_int_from_range(genrange[0], genrange[1]) for _ in range(n)
            )

    def generate_normal(
        self, n: int, genrange: tuple[float | int, float | int] = None
    ) -> Generator[float, None, None]:
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"param n must be positive int, given: {n} ({type(n)})")

        if (
            genrange is not None
            and not isinstance(genrange, tuple)
            and len(genrange) != 2
        ):
            raise ValueError("param range must be a tuple (low, high) or None")

        for _ in range(n):
            u1 = self.next_float_from_range(0, 1)
            u2 = self.next_float_from_range(0, 1)
            z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            yield (
                z0
                if genrange is None
                else genrange[0] + z0 * (genrange[1] - genrange[0])
            )

    def generate_bits(self, n: int) -> Generator[int, None, None]:
        """Generate n bits (ints in {0, 1})"""
        return self.generate_ints(n, (0, 1))


if __name__ == "__main__":
    lcg = LinearCongruentialGenerator()
    print("Next int:")
    for num in lcg.generate_ints(15):
        print(num)

    print("\nNext int from range [0; 255]")
    for num in lcg.generate_ints(15, (0, 255)):
        print(num)

    print("\nNext float from range [0; 1]")
    for _ in range(15):
        print(lcg.next_float_from_range(0, 1))

    print("\nGenerate normal")
    for num in lcg.generate_normal(15, (3, 5)):
        print(num)

    print("\nBits")
    for bit in lcg.generate_bits(15):
        print(bit)
