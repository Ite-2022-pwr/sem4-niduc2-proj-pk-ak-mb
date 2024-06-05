def save_to_csv(data, filename):
    with open(filename, "w") as file:
        print(f"Saving data to: {filename} started")
        for row in data:
            file.write(",".join(map(str, row)))
            file.write("\n")
        file.close()
        print(f"Saving data to: {filename} finished")
