import random
import numpy as np
from bch import Bch
from gf import GaloisField, GF2Polynomial, Gf2mPoly

# Inicjalizacja parametrów
m = 6  # Stopień rozszerzenia ciała GF(2^m)
t = 15  # Zdolność korekcji błędów
polynomial_str = "1100001"  # Reprezentacja wielomianu tworzącego ciała GF(2^m)

# Inicjalizacja ciała GF(2^m)
finite_field = GaloisField(m, polynomial_str)

# Inicjalizacja kodu BCH
bch_code = Bch(finite_field, t)

# Generowanie losowej wiadomości do zakodowania
message = list(np.random.randint(2, size=bch_code.dataword_length))

def flip_random_bits(word, num_errors):
    """Flips a specified number of random bits in the given word."""
    error_locations = random.sample(range(0, len(word)), num_errors)
    for location in error_locations:
        word[location] ^= 1

# Testowanie kodu BCH dla różnych liczby błędów
for num_errors in range(t):
    # Kodowanie wiadomości
    codeword = bch_code.encode(message)
    
    # Wprowadzenie błędów do kodu
    flip_random_bits(codeword, num_errors)
    
    # Dekodowanie wiadomości
    decoded_message = bch_code.decode(codeword)
    
    # Wyświetlenie wyników
    print("Original message:  ", message)
    print("Decoded message:   ", decoded_message)
    print("Number of errors:  ", num_errors)
    print()

# Testowanie kodu BCH dla liczby błędów przekraczającej zdolność korekcji błędów
codeword = bch_code.encode(message)
flip_random_bits(codeword, t + 1)
decoded_message = bch_code.decode(codeword)

# Wyświetlenie wyników
print("Original message:  ", message)
print("Decoded message with too many errors: ", decoded_message)
