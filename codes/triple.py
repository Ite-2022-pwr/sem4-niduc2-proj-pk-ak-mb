import sys
import os

from numpy import array
from collections import Counter

# Pobieranie ścieżki do bieżącego katalogu skryptu
current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_script_dir))

# Importowanie klasy CoderDecoder z modułu codes
from functools import reduce
from codes import CoderDecoder


class TripleCoderDecoder(CoderDecoder):
    def __init__(self):
        super().__init__(name="triple_encoder_decoder")

    def encode(self, message_bits: list[int]) -> list[int]:
        encoded_message = []
        for bit in message_bits:
            encoded_message.extend([bit] * 3)  # Podwaja każdy bit
        return encoded_message

    def decode(self, encoded_message_bits: list[int]) -> list[int]:
        decoded_message = []
        for i in range(0, len(encoded_message_bits), 3):
            chunk = encoded_message_bits[i : i + 3]
            decoded_message.append(max(set(chunk), key=chunk.count))  # Reguła większościowa
        return decoded_message

    def __str__(self) -> str:
        return "TripleCoderDecoder"


if __name__ == "__main__":
    original_message = [1, 0, 1, 0, 0, 1, 1, 1]
    coder_decoder_instance = TripleCoderDecoder()
    encoded_message = coder_decoder_instance.encode(original_message)
    decoded_message = coder_decoder_instance.decode(encoded_message)
    
    # Wypisywanie wyników
    print(f"Oryginalna wiadomość: {original_message}")
    print(f"Zakodowana wiadomość: {encoded_message}")
    print(f"Zdekodowana wiadomość: {decoded_message}")
    print(f"Czy oryginalna wiadomość jest równa zdekodowanej? {original_message == decoded_message}")
