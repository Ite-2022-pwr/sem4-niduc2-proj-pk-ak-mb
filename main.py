import matplotlib.pyplot as plt

import utils.rng as rng

if __name__ == "__main__":
    lcg = rng.LinearCongruentialGenerator()
    nums = list(map(int, lcg.generate_normal(5000, (0, 255))))
    plt.hist(nums)
    plt.show()
    for i in nums:
        print(i)