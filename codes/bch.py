import sys
import os
import galois

__SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(__SCRIPT_DIR))

from functools import reduce
from codes import CoderDecoder
#class HammingCoderDecoder(CoderDecoder):
def min_polynomial(GF, n):
    minimal_polynomials = []
    for i in range (1, n+1):
        min_pol = GF.minimal_poly(GF.primitive_element**i)
        minimal_polynomials.append(min_pol)
    return minimal_polynomials

def generator_poly(minimal_polynomials, d):
    g = 1
    processed_polynomials = []

    if d%2 == 1:
        d -= 1

    for i in range (0,d):
        minimal = minimal_polynomials[i]
        if minimal in processed_polynomials:
            continue
        g *= minimal
        processed_polynomials.append(minimal)
    return g

def encoding(q, m, message):
    n = q ** m - 1
    GF = galois.GF(q ** m)
    min_pol = min_polynomial(GF, n)
    generated_poly = generator_poly(min_pol, 8)

    message_GF = GF(message)
    message_polly = galois.Poly(message_GF, order="asc")

    #print(type(generated_poly))
    #print(type(message_polly))

    codded_poly = generated_poly * message_polly
    #print(codded_poly)

def encoding(q, m, message):
    n = q ** m - 1
    GF = galois.GF(q ** m)
    min_pol = min_polynomial(GF, n)
    generated_poly = generator_poly(min_pol, 10)
    generated_coeffs = generated_poly.coefficients()

    GF_2 = galois.GF(q ** m)

    generated_GF = GF([1,1,1,0,1,1,0,1,0,0,1])
    generated_poly = galois.Poly(generated_GF, order="desc")
    print(generated_poly)

    message_GF = GF(message)
    message_poly = galois.Poly(message_GF, order="desc")
    print(message_poly)

    #print(type(generated_poly))
    #print(type(message_polly))

    codded_poly = generated_poly * message_poly
    print(codded_poly)

def splitting_message(message):
    text = []
    while message>0:
        text.append(message%10)
        message = message // 10
    text.reverse()
    return text

q = 2
m = 4
message = 101101110111101111101
message = splitting_message(message)
encoding(2, 4, message)

