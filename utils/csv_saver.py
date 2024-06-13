def save_to_csv(data: any, filename: str) -> None:
    if filename[-4:] != ".csv":
        filename += ".csv"
    try:
        with open(filename, "w") as file:
            print(f"Saving data to: {filename} started")
            for row in data:
                file.write(",".join(map(str, row)))
                file.write("\n")
        print(f"Saving data to: {filename} finished")
    except Exception as e:
        print(f"Error while handling file: {filename}")
        print(e)
        return
