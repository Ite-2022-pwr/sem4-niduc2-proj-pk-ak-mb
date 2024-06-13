import matplotlib.pyplot as plt
import pandas as pd


def import_csv_to_panadas(input_file_name: str) -> pd.DataFrame:
    return pd.read_csv(input_file_name)


def generate_plot_for_triple_from_csv(
    output_file_name: str, input_data: pd.DataFrame
) -> None:
    print("to be implemented")


if __name__ == "__main__":
    data = import_csv_to_panadas("test.csv")
    for column in data.columns:
        print(column)
