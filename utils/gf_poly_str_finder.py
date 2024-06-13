from sympy import symbols, GF, Poly, sympify


def int_to_binary_string(number):
    """
    Konwertuje liczbę całkowitą na jej zapis jako string liczby binarnej.

    Args:
    - number (int): Liczba całkowita do konwersji.

    Returns:
    - str: String reprezentujący liczbę binarną.
    """
    return bin(number)[2:]  # Zwraca string liczby binarnej, pomijając prefix '0b'


def generate_polynomial_string(degree, coefficients):
    """
    Generuje string reprezentujący wielomian o określonym stopniu i współczynnikach.

    Args:
    - degree (int): Stopień wielomianu.
    - coefficients (str): String zawierający współczynniki wielomianu jako 0 i 1.

    Returns:
    - str: String reprezentujący wielomian.
    """
    terms = []

    for i, coeff in enumerate(coefficients):
        if coeff == "1":
            if degree - i == 0:
                terms.append("1")
            else:
                terms.append(f"x**{degree-i}")

    return " + ".join(terms)


def find_irreducible_polynomial_str(m):
    x = symbols("x")
    field = GF(2)
    plynomial_number_str = ""
    for i in range(2**m, 2 ** (m + 1)):
        polynomial_number_str = int_to_binary_string(i)
        poly = Poly(
            sympify(generate_polynomial_string(m, polynomial_number_str)),
            domain=field,
        )
        if poly.is_irreducible:
            return polynomial_number_str


if __name__ == "__main__":
    print(find_irreducible_polynomial_str(6))
