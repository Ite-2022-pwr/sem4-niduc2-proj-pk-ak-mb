# Import libraries
import datetime
import textwrap
import time

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits import mplot3d
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # load data from csv
    data = pd.read_csv("test.csv", sep=";", low_memory=False, decimal=",")

    # write all data to new data frame
    new_data = pd.DataFrame()

    # Creating dataset from loaded csv
    x = data["0-1 err"].astype(float)
    y = data["0-1 err rep"].astype(float)
    z = data["readable/all"].astype(float)

    new_data["x"] = x
    new_data["y"] = y
    new_data["z"] = z

    # Normalize the color scale from 0 to 1
    norm = plt.Normalize(0, 1)

    # Creating a custom color map
    colors = [(0, "#0022EE"), (0.5, "#0ADD08"), (1, "#FF272A")]
    my_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

    # Creating figure
    fig = plt.figure(figsize=(20, 20))
    ax = plt.axes(projection="3d")

    # Add x, y gridlines
    ax.grid(b=True, color="grey", linestyle="-.", linewidth=0.3, alpha=0.2)

    # Creating plot
    sctt = ax.scatter3D(x, y, z, alpha=0.8, c=z, cmap=my_cmap, marker="^", norm=norm)

    # Wrapping long title and labels
    title = "Wykres zależności między szansą na błąd i na jego powtórzenie do proporcji odczytywalnych pakietów w stosunku do wszystkich pakietów, dla kodu Hamminga(7,4)"
    ax.set_title("\n".join(textwrap.wrap(title, 60)), fontweight="bold", fontsize=20)

    ax.set_xlabel("Szansa na błąd", fontweight="bold")
    ax.set_ylabel("Szansa na powtórzenie ", fontweight="bold")
    ax.set_zlabel(
        "proporcja odczytywalnych pakietów(dobre+naprawione) do wszystkich",
        fontweight="bold",
    )

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    fig.colorbar(sctt, ax=ax, aspect=3)

    # show plot
    # plt.show()
    # save plot
    # get today date and time
    now = datetime.datetime.now()
    date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    plt.savefig(f"3dplot_{date_time}.png", bbox_inches="tight")

    # save new data to csv without index, column name and with comma as decimal separator, tab as separator
    new_data.to_csv(f"new_data_{date_time}.csv", sep=";", index=False, decimal=",")
