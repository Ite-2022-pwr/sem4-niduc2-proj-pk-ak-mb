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
    def __init__(self, total_bits: int = 12, data_bits: int = 5) -> None:
        super().__init__(name = "bch")
        self.q: int = 2
        self.n: int = total_bits                          # Length of the code
        self.d: int = total_bits - data_bits              # Minimum number of errors
        self.t = (self.d - 1) // 2
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

        generated_GF = GF([1,1,1,0,1,1,0,1,0,0,1])
        generated_poly = galois.Poly(generated_GF, order="desc")
        print(generated_poly)

        message_GF = GF(message)
        message_poly = galois.Poly(message_GF, order="desc")
        print(message_poly)

        #print(type(generated_poly))
        #print(type(message_polly))

        codded_poly = generated_poly * message_poly
        codded_poly_coeffs = codded_poly.coefficients()
        #print(codded_poly)
        #print(codded_poly_coeffs)
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
        received_array = np.array(received_vector, dtype=object)  # Convert to Galois Field array

        for i in range(1, 2 * self.t + 1):
            alpha_i = alpha ** i
            #print(type(alpha_i))
            alpha_i_poly = galois.Poly(alpha_i, order="desc")
            #print(type(alpha_i_poly))
            syn = self.eval(received_array, alpha_i_poly)
            syndrome.append(syn)
            print(type(syn))
        #syndrome = self.reverse(syndrome)
        return syndrome        

    def reverse(self, array):
        reversed = []
        for i in range (len(array) - 1, -1, -1):
            reversed.append(array[i])
        return reversed

    def peterson(self, syndromes):
        S_matrix = self.generate_matrix_S(syndromes)
        C_matrix = self.generate_matrix_C(syndromes)
        lambda_matrix = self.generate_matrix_lambda()
        self.calculate_lambda_matrix(S_matrix, C_matrix, lambda_matrix)

    def generate_matrix_S(self, syndromes):
        S_matrix = np.zeros((self.t, self.t))
        for i in range(self.t):
            row = []
            for j in range(self.t):
                S_matrix[i][j] = syndromes[(i+j)]
        return S_matrix
    
    def generate_matrix_C(self, syndromes):
        C_matrix = np.zeros((self.t, 1))
        for i in range(self.t):
            row = []
            for j in range(1):
                C_matrix[i][j] = syndromes[self.t + i + j]
        return C_matrix
    
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
message = 11011
message = BCH.splitting_message(message)
encoded_message = BCH.encoding(message)
synd = BCH.syndromes([1,0,0,1,1,1,0,0,0,1,1,0,1,0,0])
print(BCH.peterson(synd))
#decoded_message = BCH.decoding(encoded_message[0], encoded_message[1])
#print(decoded_message)
