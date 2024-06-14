import numpy as np

from codes import CoderDecoder
from gf import GaloisField, GF2Polynomial, Gf2mPoly


def _generator_poly(field: GaloisField, num_roots: int) -> GF2Polynomial:
    seen_conjugates = set()
    generator_polynomial = GF2Polynomial([1])

    for root_index in range(num_roots):
        power = 2 * root_index + 1
        if power in seen_conjugates:
            continue
        seen_conjugates.update(field.conjugates(power))
        root = field.get_element(power)
        minimal_poly = field.min_polynomial(root)
        generator_polynomial *= minimal_poly
    return generator_polynomial


class BchCoderDecoder(CoderDecoder):
    def __init__(
        self, finite_field: GaloisField, error_correction_capability: int, name: str
    ) -> None:
        super().__init__(name)
        self.finite_field = finite_field  # GF(2^m)
        self.error_correction_capability = (
            error_correction_capability  # error correction capability
        )
        self.codeword_length = 2**finite_field.m - 1  # codeword length
        self.generator_polynomial = generator_polynomial = _generator_poly(
            finite_field, error_correction_capability
        )  # generator polynomial
        self.minimum_distance = generator_polynomial.hamming_weight()  # see Theorem 3.1
        self.dataword_length = (
            self.codeword_length - generator_polynomial.degree
        )  # dataword length
        self.num_parity_digits = (
            self.codeword_length - self.dataword_length
        )  # number of parity-check digits

        self.minimum_polynomials = []
        for i in range(1, 2 * error_correction_capability + 1):
            alpha_i = finite_field.get_element(i)  # element alpha^i
            self.minimum_polynomials.append(finite_field.min_polynomial(alpha_i))

    def encode(self, dataword: list) -> list:
        assert len(dataword) == self.dataword_length
        padded_message = GF2Polynomial(
            [0] * self.num_parity_digits + dataword
        )  # x^(n-k)*d(x)
        parity_check = padded_message % self.generator_polynomial  # rho(x)

        num_zero_padding = self.num_parity_digits - parity_check.degree - 1
        return dataword + parity_check.coefs + [0] * num_zero_padding

    def syndrome(self, received_codeword: list) -> np.array:
        assert len(received_codeword) == self.codeword_length, "Invalid codeword length"
        received_polynomial = GF2Polynomial(received_codeword)
        syndromes = np.zeros(
            2 * self.error_correction_capability, dtype=self.finite_field.dtype
        )

        for i in range(1, 2 * self.error_correction_capability + 1):
            remainder_poly = (
                received_polynomial % self.minimum_polynomials[i - 1]
            )  # a polynomial over GF(2)
            remainder_gf2m_poly = Gf2mPoly(
                self.finite_field, remainder_poly
            )  # cast to a GF(2^m) polynomial
            alpha_i = self.finite_field.get_element(i)  # element alpha^i
            syndromes[i - 1] = remainder_gf2m_poly.eval(alpha_i)  # b_i(alpha^i)

        return syndromes

    def err_loc_polynomial(self, syndromes: np.array) -> Gf2mPoly:
        num_rows = self.error_correction_capability + 2

        mu_values = np.zeros(num_rows)
        mu_values[0] = -0.5
        mu_values[1:] = np.arange(0, self.error_correction_capability + 1)

        error_locator_polynomials = [
            Gf2mPoly(self.finite_field, [self.finite_field.unit]),
            Gf2mPoly(self.finite_field, [self.finite_field.unit]),
            Gf2mPoly(self.finite_field, [self.finite_field.unit, syndromes[0]]),
        ]

        discrepancies = np.zeros(num_rows, dtype=self.finite_field.dtype)
        discrepancies[0] = self.finite_field.unit
        discrepancies[1] = syndromes[0]

        row = 2
        while row <= self.error_correction_capability:
            mu = mu_values[row]
            two_mu = int(2 * mu)

            discrepancies[row] = syndromes[two_mu]  # e.g., for mu=1, pick S[2]
            for j, coef in enumerate(error_locator_polynomials[row].coefficients[1:]):
                if coef:
                    discrepancies[row] = self.finite_field.dtype(
                        discrepancies[row]
                    ) ^ self.finite_field.dtype(
                        self.finite_field.multiply(coef, syndromes[two_mu - j - 1])
                    )

            if discrepancies[row] == 0:
                error_locator_polynomials.append(error_locator_polynomials[row])
            else:
                row_rho = 0  # row number where mu=rho
                max_diff = -2  # maximum diff "2*rho - sigma[row_rho].degree"
                for j in range(row - 1, -1, -1):  # rows prior to the μ-th row
                    if discrepancies[j] != 0:  # discrepancy is not zero
                        diff = (2 * mu_values[j]) - error_locator_polynomials[j].degree
                        if diff > max_diff:
                            max_diff = diff
                            row_rho = j
                rho = mu_values[row_rho]  # value of mu at the rho-th row

                discrepancy_ratio = self.finite_field.divide(
                    discrepancies[row], discrepancies[row_rho]
                )
                x_shifted = Gf2mPoly(
                    self.finite_field,
                    int(2 * (mu - rho)) * [0] + [self.finite_field.unit],
                )
                new_polynomial = error_locator_polynomials[row] + (
                    x_shifted * discrepancy_ratio * error_locator_polynomials[row_rho]
                )
                error_locator_polynomials.append(new_polynomial)

            row += 1

        return error_locator_polynomials[row]

    def err_loc_numbers(self, error_locator_polynomial: Gf2mPoly) -> list:
        error_positions = []
        for elem in self.finite_field.table[1:]:
            if error_locator_polynomial.eval(elem) == self.finite_field.zero:
                error_positions.append(elem)
        return [self.finite_field.inverse(x) for x in error_positions]

    def decode(self, received_codeword: list[int]) -> tuple[list[int], int]:
        syndromes = self.syndrome(received_codeword)
        error_positions = []
        if np.any(syndromes):
            error_locator_polynomial = self.err_loc_polynomial(syndromes)
            error_positions = self.err_loc_numbers(error_locator_polynomial)
            error_exponents = [
                self.finite_field.get_exponent(x) for x in error_positions
            ]
            for exp in error_exponents:
                received_codeword[self.finite_field.dtype(exp)] ^= 1
        return received_codeword[: self.dataword_length], len(error_positions)


if __name__ == "__main__":
    bch = BchCoderDecoder(GaloisField(4), 3, "BCH(15, 11)")
