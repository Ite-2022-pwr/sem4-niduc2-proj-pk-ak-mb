import os
import time


class LinearCongruentialGenerator:
    """Pseudorandom number generator"""
    
    def __init__(self, a: int = 2137, c: int = 69, m: int = 2**13, seed: int = None):
        """LCG constructor
        :param: a - the multiplier
        :param: c - the increment
        :param: m - the modulus
        :param: seed - the start value
        """

        assert 0 < m, "param m (modulus) must be a positive number"
        assert 0 < a < m, "param a (multiplier) must be 0 < a < m"
        assert 0 < c < m, "param c (increment) must be 0 < c < m"

        self.__multiplier = a
        self.__increment = c
        self.__modulus = m

        if seed is None:
            self.__x0 = int(os.getpid() + time.time())
        else:
            self.__x0 = seed

        self.__x_next = (self.__multiplier * self.__x0 + self.__increment) % self.__modulus

    def next_int(self) -> int:
        """Generates pseudo random integer"""
        self.__x_next = (self.__multiplier * self.__x_next + self.__increment) %  self.__modulus
        return self.__x_next


if __name__ == '__main__':
    lcg = LinearCongruentialGenerator()
    for i in range(15):
        print(lcg.next_int())    
