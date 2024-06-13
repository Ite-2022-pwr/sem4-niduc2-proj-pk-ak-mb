import random
import numpy as np
from bch import BchCoderDecoder as Bch
from gf import GaloisField, GF2Polynomial, Gf2mPoly


if __name__ == "__main__":
    # Inicjalizacja parametrów
    m = 6  # Stopień rozszerzenia ciała GF(2^m)
    t = 3  # Zdolność korekcji błędów
    polynomial_str = "1100001"  # Reprezentacja wielomianu tworzącego ciała GF(2^m)

    # Inicjalizacja ciała GF(2^m)
    finite_field = GaloisField(m, polynomial_str)

    # Inicjalizacja kodu BCH
    bch_code = Bch(finite_field, t, "BCH(6, 15)")

    # Generowanie losowej wiadomości do zakodowania
    message = list(np.random.randint(2, size=bch_code.dataword_length))

    def flip_random_bits(word, num_errors):
        """Flips a specified number of random bits in the given word."""
        error_locations = random.sample(range(0, len(word)), num_errors)
        for location in error_locations:
            word[location] ^= 1

    # Testowanie kodu BCH dla różnych liczby błędów
    for num_errors in range(t * 2):
        print("Original message:  ", message)
        # Kodowanie wiadomości
        codeword = bch_code.encode(message)
        print("Encoded message:   ", codeword)

        # Wprowadzenie błędów do kodu
        flip_random_bits(codeword, num_errors)
        print("Received message:  ", codeword)
        # Dekodowanie wiadomości
        decoded_message, errors_detected = bch_code.decode(codeword)

        # Wyświetlenie wyników

        print("Decoded message:   ", decoded_message)
        print("Number of errors:  ", num_errors)
        print("Number of errors detected:  ", errors_detected)
        print("Decoding successful: ", message == decoded_message)
        print()

    # Testowanie kodu BCH dla liczby błędów przekraczającej zdolność korekcji błędów
    codeword = bch_code.encode(message)
    flip_random_bits(codeword, t + 1)
    decoded_message, errors_detected = bch_code.decode(codeword)

    # Wyświetlenie wyników
    print("Original message:  ", message)
    print("Decoded message with too many errors: ", decoded_message)
    print("Number of errors detected:  ", errors_detected)