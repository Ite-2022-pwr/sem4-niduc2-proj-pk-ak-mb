def save_to_csv(data, filename):
    with open(filename, "w") as file:
        for row in data:
            file.write(",".join(map(str, row)))
            file.write("\n")
