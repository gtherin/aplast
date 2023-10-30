import numpy as np
import matplotlib.pyplot as plt
import os


# gravity acceleration
g = 9.80665  # m/s2


# density of the water
r_water = 1025  # kg/m3
pressure_0 = 101325  # Pa

# density of the ballast (lead)
r_ballast = 11000  # kg/m3
# density of the neoprene
r_neo = 1230  # kg/m3
# density of neoprene foam
r_nfoam = 170  # kg/m3


# Get package colors
background_color = "#F0FDFA11"  # cdcdcd
background_color2 = "#4F77AA11"


def get_color(discipline):
    colors = {
        "swimming": "#581845",
        "cycling": "#C70039",
        "running": "#FF5733",
        "axis": "#4F77AA",
    }
    return colors[discipline] if discipline in colors else "black"


def set_style():
    plt.rcParams["axes.grid"] = True
    plt.rcParams["axes.edgecolor"] = get_color("axis")
    plt.rcParams["axes.labelcolor"] = get_color("axis")
    plt.rcParams["axes.titlecolor"] = get_color("axis")
    plt.rcParams["axes.facecolor"] = background_color
    plt.rcParams["figure.edgecolor"] = get_color("axis")
    plt.rcParams["figure.facecolor"] = background_color
    plt.rcParams["grid.color"] = "white"
    plt.rcParams["legend.facecolor"] = background_color
    plt.rcParams["legend.edgecolor"] = background_color
    # plt.rcParams["text.color"] = "white"
    plt.rcParams["xtick.color"] = get_color("axis")
    plt.rcParams["ytick.color"] = get_color("axis")

    plt.rcParams["font.size"] = 16
    # plt.rcParams["axes.labelsize"] = "medium"
    plt.rcParams["lines.linewidth"] = 4

    # ax.grid(True, axis="y", color="white")

    from cycler import cycler

    # mpl.rcParams['axes.prop_cycle'] = cycler(color='bgrcmyk')
    # mpl.rcParams['axes.prop_cycle'] = cycler(color='bgrcmyk')
    plt.rcParams["axes.prop_cycle"] = cycler(
        color=[get_color(c) for c in ["swimming", "cycling", "running", "The end"]]
    )


set_style()


def get_file(filename):
    for d in [".", "aplast/notebooks", "../aplast/notebooks", "aplast/aplast", "../aplast/aplast", "../aplast"]:
        if os.path.exists(f"{d}/{filename}"):
            return f"{d}/{filename}"
