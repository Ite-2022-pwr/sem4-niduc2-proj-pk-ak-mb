def binary_representation(num, n) -> str:
    binary = bin(num)[2:]  # Convert to binary, remove '0b' prefix
    padded_binary = binary.zfill(n)  # Pad from the left side
    return padded_binary
