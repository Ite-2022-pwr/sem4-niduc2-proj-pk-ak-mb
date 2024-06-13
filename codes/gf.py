import random
import numpy as np
from typing import Union

# Funkcje pomocnicze
def bit_string_to_array(bit_string):
    return np.array(list(map(int, bit_string)), dtype=np.uint8)

def generate_galois_field_matrix(m, polynomial_string):
    polynomial = bit_string_to_array(polynomial_string)
    assert (len(polynomial) == m + 1 and polynomial[-1] == 1), \
        "The primitive polynomial must have degree m"
    feedback_weights = np.copy(polynomial[:-1])
    feedback_weights[0] = 0
    gf_matrix = np.zeros((2**m, m), dtype=np.uint8)
    gf_matrix[1, 0] = 1
    for i in range(1, 2**m - 1):
        last_bit = gf_matrix[i, -1]
        gf_matrix[i + 1, :] = np.logical_xor(np.roll(gf_matrix[i, :], 1), last_bit * feedback_weights)
    return gf_matrix

# Klasa GF
class GaloisField:
    def __init__(self, m, polynomial_string, dtype=np.uint32) -> None:
        if m <= 1:
            raise ValueError("m must be > 1")
        self.m = m
        self.polynomial_string = polynomial_string
        self.dtype = dtype
        self.two_to_m_minus_one = 2**m - 1
        self.table = self._generate_table()
        self.zero = self.table[0]
        self.unit = self.table[1]
        self.alpha = self.table[2]
        self.inverse_table = self._generate_inverse_table(self.table)

    def _generate_table(self):
        m = self.m
        polynomial_string = self.polynomial_string
        max_m = 8 * np.dtype(self.dtype).itemsize
        assert m <= max_m, f"Implementation works up to m={max_m} only"
        polynomial = int(polynomial_string[:-1], 2)
        gf_table = np.zeros(2**m, dtype=self.dtype)
        gf_table[1] = 1 << (m - 1)
        for i in range(1, 2**m - 1):
            gf_table[i + 1] = (gf_table[i] >> 1) ^ ((gf_table[i] & 1) * polynomial)
        return gf_table

    def _generate_inverse_table(self, gf_table):
        assert gf_table[0] == 0, \
            "The GF table must have the zero element at index 0"
        inverse_table = np.zeros(gf_table.shape, dtype=gf_table.dtype)
        for alpha_i in range(len(gf_table)):
            inverse_table[alpha_i] = np.argwhere(gf_table == alpha_i)[0][0]
        return inverse_table

    def get_element(self, i):
        return self.table[(i % self.two_to_m_minus_one) + 1]

    def get_exponent(self, beta):
        assert beta != 0, "beta must be non-zero"
        return self.inverse_table[beta] - 1

    def index(self, beta):
        return self.inverse_table[beta]

    def multiply(self, a, b):
        if a == 0 or b == 0:
            return 0
        exp_a = self.get_exponent(a)
        exp_b = self.get_exponent(b)
        return self.get_element(exp_a + exp_b)

    def inverse(self, a):
        exp_a = self.get_exponent(a)
        return self.get_element(self.two_to_m_minus_one - exp_a)

    def divide(self, a, b):
        return self.multiply(a, self.inverse(b))

    def conjugates(self, i):
        assert i <= (self.two_to_m_minus_one - 1), \
            "The max element in GF(2^m) is alpha^(2^m-2)"
        conjugate_list = [i]
        max_distinct_conjugates = self.m
        for j in range(1, max_distinct_conjugates + 1):
            exponent = (i * (2**j)) % self.two_to_m_minus_one
            if exponent in conjugate_list:
                break
            conjugate_list.append(exponent)
        return sorted(conjugate_list)

    def min_polynomial(self, beta):
        if beta == 0:
            return GF2Polynomial([0, 1])
        exp_beta = self.get_exponent(beta)
        conjugate_list = self.conjugates(exp_beta)
        product = Gf2mPoly(self, [self.unit])
        for exp in conjugate_list:
            a = Gf2mPoly(self, [self.get_element(exp), self.unit])
            product *= a
        return GF2Polynomial([self.index(x) for x in product.coefficients])

# Klasy Gf2Poly i Gf2mPoly
def is_gf2_polynomial(coefficients: list) -> bool:
    return set(coefficients).issubset({0, 1})

def is_gf2m_polynomial(gf: GaloisField, coefficients: list) -> bool:
    return all([coef in gf.table for coef in coefficients])

def cut_trailing_gf2_polynomial_zeros(coefficients: list) -> list:
    return coefficients[:(len(coefficients) - coefficients[::-1].index(1))] if any(coefficients) else []

def cut_trailing_gf2m_polynomial_zeros(coefficients: list) -> list:
    trailing_zeros = next((i for i, x in enumerate(reversed(coefficients)) if x), None)
    return coefficients[:(len(coefficients) - trailing_zeros)] if trailing_zeros is not None else []

def add_gf2_polynomial(a: list, b: list) -> list:
    n_pad = len(a) - len(b)
    if n_pad > 0:
        b = b + n_pad * [0]
    elif n_pad < 0:
        a = a + (-n_pad * [0])
    return [x ^ y for x, y in zip(a, b)]

def add_gf2m_polynomial(gf: GaloisField, a: list, b: list) -> list:
    n_pad = len(a) - len(b)
    if n_pad > 0:
        b = b + n_pad * [0]
    elif n_pad < 0:
        a = a + (-n_pad * [0])
    return [x ^ y for x, y in zip(a, b)]

def multiply_gf2_polynomial(a: list, b: list) -> list:
    product = (len(a) + len(b) - 1) * [0]
    for i, a_i in enumerate(a):
        for j, b_j in enumerate(b):
            product[i + j] ^= a_i & b_j
    return product

def multiply_gf2m_polynomial(gf, a, b):
    product = (len(a) + len(b) - 1) * [0]
    for i, a_i in enumerate(a):
        for j, b_j in enumerate(b):
            product[i + j] ^= gf.multiply(a_i, b_j)
    return product

def remainder_gf2_polynomial(a: list, b: list, deg_a: int, deg_b: int) -> list:
    if not any(a):
        return []
    if deg_a < deg_b:
        return a
    length_a = len(a)
    length_b = len(b)
    remainder = a.copy()
    nxors = length_a - length_b + 1
    for i in np.arange(length_a, length_a - nxors, -1):
        if remainder[i - 1]:
            remainder[(i - length_b):i] = np.bitwise_xor(remainder[(i - length_b):i], b)
    return remainder

class GF2Polynomial:
    def __init__(self, coefficients: list) -> None:
        if not is_gf2_polynomial(coefficients):
            raise ValueError("Not a polynomial over GF(2)")
        self.coefs = cut_trailing_gf2_polynomial_zeros(coefficients)
        self.degree = len(self.coefs) - 1 if any(self.coefs) else -1

    def __add__(self, other):
        return GF2Polynomial(add_gf2_polynomial(self.coefs, other.coefs))

    def __mul__(self, other):
        if isinstance(other, GF2Polynomial):
            return GF2Polynomial(multiply_gf2_polynomial(self.coefs, other.coefs))
        elif other in [0, 1]:
            return GF2Polynomial([other * y for y in self.coefs])
        else:
            raise ValueError("* expects a GF(2) polynomial or scalar")

    def __mod__(self, other):
        return GF2Polynomial(
            remainder_gf2_polynomial(self.coefs, other.coefs, self.degree, other.degree))

    def __eq__(self, other: object) -> bool:
        return self.coefs == other.coefs

    def hamming_weight(self):
        return sum(self.coefs)
    
class Gf2mPoly:
    def __init__(self, field: GaloisField, coefficients: Union[list, GF2Polynomial]) -> None:
        if isinstance(coefficients, GF2Polynomial):
            coefficients = [field.table[x] for x in coefficients.coefs]

        if not is_gf2m_polynomial(field, coefficients):
            raise ValueError("Not a polynomial over GF(2^m)")

        self.coefficients = cut_trailing_gf2m_polynomial_zeros(coefficients)
        self.degree = len(self.coefficients) - 1 if any(self.coefficients) else 0
        self.field = field

    def __add__(self, other):
        if isinstance(other, Gf2mPoly):
            return Gf2mPoly(self.field, add_gf2m_polynomial(self.field, self.coefficients, other.coefficients))
        else:
            raise ValueError("Addition is defined between two GF(2^m) polynomials")

    def __mul__(self, other):
        if isinstance(other, Gf2mPoly):
            return Gf2mPoly(self.field, multiply_gf2m_polynomial(self.field, self.coefficients, other.coefficients))
        elif other in self.field.table:
            return Gf2mPoly(self.field, [self.field.multiply(other, coeff) for coeff in self.coefficients])
        else:
            raise ValueError("Multiplication is defined between a GF(2^m) polynomial and another GF(2^m) polynomial or scalar")

    def __eq__(self, other: object) -> bool:
        return self.coefficients == other.coefficients

    def eval(self, x):
        assert x in self.field.table

        if x == self.field.zero:
            return self.coefficients[0]

        i = self.field.get_exponent(x)
        result = 0
        for j, coef in enumerate(self.coefficients):
            if coef:
                result ^= self.field.multiply(coef, self.field.get_element(i * j))
        return result
