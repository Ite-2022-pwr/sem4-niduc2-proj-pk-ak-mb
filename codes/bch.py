import sys
import os
import galois
from galois import Poly, GF
from sympy.abc import x, alpha
from sympy import Matrix
import numpy as np
from sympy import Symbol, Poly
from sympy import GF, Poly, Pow, Add, Symbol
from sympy.polys.galoistools import gf_add, gf_mul

__SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(__SCRIPT_DIR))

from functools import reduce
from codes import CoderDecoder

class BCHCoderDecoder(CoderDecoder):
    def __init__(self, total_bits: int = 15, data_bits: int = 5, target_error: int = 1) -> None:
        #super().__init__(name = "bch")
        super().__init__()
        self.q: int = 2
        self.n: int = total_bits                          # Length of the code
        self.d: int = total_bits - data_bits              # Minimum number of errors
        self.t = target_error                             # Target error correction capability in bits
        #self.d: int = target_error * 2 + 1                # min Hamming distance d ≤ q^m − 1
        self.d: int = 7
        self.t: int = (self.d - 1) // 2
        self.k: int = 0
        self.generated_poly = None  # Placeholder for r_poly
        self.min_poly = None

        #self.m: int = self.find_m()
        self.m: int =  4

    def find_m(self):
        m = 2
        while(True):
            result = self.q ** m - 1                                   # Iteruj przez potencjalne wartości m 
            if (result) >= self.n:       # Sprawdź, czy n = q^m - 1 spełnione 
                return m  
            m += 1

    def min_polynomial(self, GF):
        minimal_polynomials = []
        for i in range(1, self.n + 1):
            min_pol = GF.minimal_poly(GF.primitive_element ** i)
            minimal_polynomials.append(min_pol)
        return minimal_polynomials

    def generator_poly(self, minimal_polynomials):
        g = 1
        processed_polynomials = []

        if self.d % 2 == 1:
            self.d -= 1

        for i in range(0, self.d):
            minimal = minimal_polynomials[i]
            if minimal in processed_polynomials:
                continue
            g *= minimal
            processed_polynomials.append(minimal)
        return g

    def encoding(self, message):
        GF = galois.GF(self.q ** self.m)
        self.min_poly = self.min_polynomial(GF)
        self.generated_poly = self.generator_poly(self.min_poly)
        generated_coeffs = self.generated_poly.coefficients()
        print(generated_coeffs)

        #generated_GF = GF(generated_coeffs)
        generated_GF = GF([1,0,1,0,0,1,1,0,1,1,1])
        generated_poly = galois.Poly(generated_GF, order="desc")
        self.k = self.n - generated_poly.degree
        print(generated_poly)

        message_GF = GF(message)
        message_poly = galois.Poly(message_GF, order="desc")
        print(message_poly)

        #print(type(generated_poly))
        #print(type(message_polly))

        codded_poly = generated_poly * message_poly
        codded_poly_coeffs = codded_poly.coefficients()
        #print(codded_poly)
        print(codded_poly_coeffs)
        return codded_poly_coeffs

    def splitting_message(self, message):
        text = []
        while message > 0:
            text.append(message % 10)
            message = message // 10
        text.reverse()
        return text
    
    def eval(self, received_array, alpha_power):
        GF = galois.GF(self.q ** self.m)
        tab = []
        tab.append(0)
        tab_gf = GF(tab)
        evaluation = galois.Poly(tab_gf, order="desc")
        for i, coefficient in enumerate(reversed(received_array)):
            tab = []
            tab.append(coefficient)
            tab_gf = GF(tab)
            coefficient = galois.Poly(tab_gf, order="desc")
            alfik = alpha_power ** i
            evaluation += coefficient * (alpha_power ** i)
        return evaluation

    def syndromes(self, received_vector):
        syndrome = []
        GF = galois.GF(self.q ** self.m)
        alpha = GF.primitive_element
        print(alpha)
        received_array = np.array(received_vector, dtype=object)  # Convert to Galois Field array

        for i in range(1, 2 * self.t + 1):
            alpha_i = alpha ** i
            print(alpha_i)
            alpha_i_poly = galois.Poly(alpha_i, order="desc")
            print(alpha_i_poly)
            syn = self.eval(received_array, alpha_i_poly)
            syndrome.append(syn)
            print(syn)
        #syndrome = self.reverse(syndrome)
        return syndrome        

    def reverse(self, array):
        reversed = []
        for i in range (len(array) - 1, -1, -1):
            reversed.append(array[i])
        return reversed

    def decoding(self, message):
        syndromes = BCH.syndromes(message)
        GF = galois.GF(self.q ** self.m)
        zero_gf = GF([0])
        zero_poly = galois.Poly(zero_gf, order="desc")
        error = self.calculate_error(syndromes)

        if error == zero_poly:
            n = self.n - len(message)
            print(n)
            return np.pad(np.array(message), (n, 0), 'constant')[:self.k]

        v = self.t
        S_matrix = self.generate_matrix_S(syndromes, v)
        S_numerix = self.convert_matrix_to_numerix(S_matrix)
        print(S_numerix)
        S_det = self.calculate_determinant(S_numerix)
        print(S_det)

        while S_det.is_zero and S_matrix.shape[0] > 1:
            v -= 1
            S_matrix = self.generate_matrix_S(syndromes, v)
            S_numerix = self.convert_matrix_to_numerix(S_matrix)
            S_det = self.calculate_determinant(S_numerix)

        C_matrix = self.generate_matrix_C(syndromes)
        lambda_matrix = self.generate_matrix_lambda()
        
        
        
        #augmented_matrix = np.hstack((S_matrix, C_matrix))
        #print(augmented_matrix)
        #reduced_matrix = self.row_reduction(augmented_matrix)
        #return reduced_matrix

        #while v > 0:
        #    detS = self.calculate_determinant(S_matrix)
        #    print(detS)
        #    if detS == 0:
        #        break
        #    v -= 1
        #    S_matrix = self.generate_matrix_S(syndromes, v)
        #    print(S_matrix)
        #self.calculate_lambda_matrix(S_matrix, C_matrix, lambda_matrix)

    def generate_matrix_S(self, syndromes, size):
        matrix = np.zeros((size, size), dtype=object)  # Użyj dtype=object, aby przechowywać dowolne obiekty, w tym wielomiany
        for i in range(size):
            for j in range(size):
                matrix[i][j] = syndromes[(i+j)]
        return matrix
    
    def convert_matrix_to_numerix(self, matrix):
        rows, cols = matrix.shape
        numerix = np.zeros((rows, cols), dtype=float)

        for i in range(rows):
            for j in range(cols):
                numerix[i][j] = matrix[i, j].coeffs
        return numerix

    def zero_matrix(self, x, y):
        GF = galois.GF(self.q ** self.m)
        zero_gf = GF([0])
        zero_poly = galois.Poly(zero_gf, order="desc")

        matrix = np.full((x, y), zero_poly, dtype=object)  # Wypełnij macierz zerowymi wielomianami
        return matrix

    def generate_matrix_C(self, syndromes):
        matrix = np.zeros((self.t, 1), dtype=object)  # Użyj dtype=object, aby przechowywać dowolne obiekty, w tym wielomiany
        for i in range(self.t):
            for j in range(1):
                matrix[i][j] = syndromes[self.t + i + j]
        return matrix
    
    def generate_matrix_lambda(self):
        lambda_matrix = np.zeros((self.t, 1))
        GF = galois.GF(self.q ** self.m)
        zero_gf = GF([0])
        zero_poly = galois.Poly(zero_gf, order="desc")

        for i in range(self.t):
            row = []
            for j in range(1):
                lambda_matrix[i][j] = zero_poly
        return lambda_matrix
    
    def calculate_determinant(self, matrix):
        determinant = np.linalg.det(matrix)
        GF = galois.GF(self.q ** self.m)
        det_gf = GF(int(determinant))
        det_poly = galois.Poly(det_gf, order="desc")
        return det_poly
    
    def calculate_error(self, syndromes):
        GF = galois.GF(self.q ** self.m)
        zero_gf = GF([0])
        error = galois.Poly(zero_gf, order="desc")
        for one_syn in syndromes:
            error += one_syn
        return error

    def calculate_lambda_matrix(self, S_matrix, C_matrix, lambda_matrix):
        inversed_S_matrix = np.linalg.inv(S_matrix)
        lambda_matrix = - np.dot(inversed_S_matrix, C_matrix)
        print(lambda_matrix)
    
    #def check_if_empty(self, matrix):
    #    lambda_matrix = np.zeros((self.t, 1))
    #    GF = galois.GF(self.q ** self.m)
    #    zero_gf = GF([0])
    #    zero_poly = galois.Poly(zero_gf, order="desc")
    #
    #    rows = len(matrix)
    #    columns = len(matrix[0])
    #
    #    for i in range(rows):
    #        for j in range(columns):
    #            element_poly = galois.Poly(GF([matrix[i][j]]), order="desc")
    #            if element_poly.equal(zero_poly):
    #                return True
    #    return False

# Instantiate the BCHCoderDecoder class
BCH = BCHCoderDecoder()
print(BCH.n)
print(BCH.m)
message = 11011
message = BCH.splitting_message(message)
message2 = 100111000110100
message2 = BCH.splitting_message(message2)
#synd = BCH.syndromes([1,0,0,1,1,1,0,0,0,1,1,0,1,0,0])
#encoded_message = BCH.encoding(message2)
#synd = BCH.syndromes([1,0,0,1,1,1,0,0,0,1,1,0,1,0,0])
print(BCH.decoding(message2))
#GF = galois.GF(BCH.q ** BCH.m)
#matrix = [
#    [galois.Poly(GF(2), order="desc"), galois.Poly(GF(3), order="desc"), galois.Poly(GF(1), order="desc"), galois.Poly(GF(1), order="desc")],
#    [galois.Poly(GF(4), order="desc"), galois.Poly(GF(1), order="desc"), galois.Poly(GF(2), order="desc"), galois.Poly(GF(2), order="desc")],
#    [galois.Poly(GF(3), order="desc"), galois.Poly(GF(2), order="desc"), galois.Poly(GF(3), order="desc"), galois.Poly(GF(3), order="desc")]
#]
#element = galois.Poly(GF(2), order="desc")
#print(element.coeffs)
#print("\n")
#print(BCH.row_reduction(matrix))
#print(BCH.peterson(synd))
#decoded_message = BCH.decoding(encoded_message[0], encoded_message[1])
#print(decoded_message)
