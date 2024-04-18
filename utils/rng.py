import os
import time

from typing import Generator

class LinearCongruentialGenerator:
    """Pseudorandom number generator"""
    
    def __init__(self, a: int = 48271, c: int = 0, m: int = 2**31 - 1, seed: int = None):
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

        self.__x_next = (self.__multiplier * self.__x0 + self.__increment) % self.__modulus

    def next_int(self) -> int:
        """Generates pseudorandom integer"""
        self.__x_next = (self.__multiplier * self.__x_next + self.__increment) %  self.__modulus
        return self.__x_next

    def next_int_from_range(self, low: int, high: int) -> int:
        """Genereate pseudorandom integer from given range [low; high]"""
        return self.next_int() % (high - low + 1) + low
    
    def generate_ints(self, n: int, genrange: tuple[int, int] = None) -> Generator[int, None, None]:
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"param n must be positive int, given: {n} ({type(n)})")
        
        if genrange is None:
            return (self.next_int() for _ in range(n))
        else:
            if not isinstance(genrange, tuple) and len(genrange) != 2:
                raise ValueError("param range must be a tuple (low, high) or None")
            return (self.next_int_from_range(genrange[0], genrange[1]) for _ in range(n))


if __name__ == '__main__':
    lcg = LinearCongruentialGenerator()
    print("Next int:")
    for num in lcg.generate_ints(15):
        print(num)

    print("Next int from range [0; 255]")
    for num in lcg.generate_ints(15, (0, 255)):
        print(num)
