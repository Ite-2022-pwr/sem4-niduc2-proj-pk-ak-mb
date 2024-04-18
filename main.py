import matplotlib.pyplot as plt

import utils.rng as rng


if __name__ == '__main__':
    lcg = rng.LinearCongruentialGenerator()
    nums = list(lcg.generate_ints(10000, (0, 255)))
    plt.hist(nums)
    plt.show()
