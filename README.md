# Niezawodność i diagnostyka układów cyfrowych 2 - projekt

## Autorzy

- [Miłosz Bedryło](https://github.com/lolex565)
- [Paulina Korus](https://github.com/paulinakorus)
- [Artur Kręgiel](https://github.com/arkregiel)

## Temat

**Transmisja w systemie FEC (Forward Error
Correction)**

- Zadanie polega na implementacji kanału komunikacyjnego (modele
BSC i Gilberta-Elliotta) i systemu transmisji FEC z różnymi kodami
korekcyjnymi (np. powielanie bitów, BCH, RS, LDPC, turbo,
fontannowe).

- Symulacyjne badanie skuteczności transmisji dla różnych parametrów
kanału (BER, błędy niezależne, błędy grupowe) i parametrów systemu
transmisji.

## Harmonogram

1. 3 marca - odwołane
2. 19 marca - wprowadzenie i wybór tematu
3. 16 kwietnia - generator liczb losowych i harmonogram projektu
4. 30 kwietnia - zaimplementowanie zachowania nadajnika i odbiornika (kodowanie)
5. 14 maja - realizacja przesyłania pakietów przez kanał z szumem
6. 28 maja - zaimplentowanie narzędzi do obliczenia statystyk i generowanie plików z wynikami
7. 11 czerwca - wstępne oddanie projektu oraz sprawozdania
8. 25 czerwca - ewentualne poprawki

## Instalowanie zależności

```
$ pip install -r requirements.txt
```

## Środowisko wirtualne

### Tworzenie środowiska wirtualnego

```
$ python3 -m venv venv
```

Lub:

```
$ virutalenv venv
```

### Aktywacja środowiska wirtualnego

#### Dla systemów Linux lub macOS

```
$ source ./venv/bin/activate
```

#### Dla systemu Windows

PowerShell:

```
PS C:\> .\venv\Scripts\Activate.ps1
```

cmd:

```
	
C:\> .\venv\Scripts\activate.bat
```

## Generowanie pliku `requirements.txt`

Jeżeli zamierzacie instalować zewnętrzne moduły to **koniecznie** używajcie wirtualnego środowiska, ponieważ w przeciwnym wypadku w pliku `requirements.txt` znajdą się **wszystkie zainstalowane** na komputerze moduły Pythona, a nie tylko te konieczne do działania projektu.

```
$ pip freeze > requirements.txt
```

## Materiały

- [Szymon Datko, Opracowanie symulatora](https://datko.pl/NiDUC2/etap1.pdf)
- [3Blue1Brown - Hamming codes part 2: The one-line implementation](https://www.youtube.com/watch?v=b3NxrZOu_CE)
