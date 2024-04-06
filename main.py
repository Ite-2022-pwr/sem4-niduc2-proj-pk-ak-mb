import utils.rng as rng


if __name__ == '__main__':
    lcg = rng.LinearCongruentialGenerator()
    for i in range(10):
        print(lcg.next_int())
