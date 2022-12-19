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


def get_body_surface_area(height: float, weight: float) -> float:
    """
    height : height of the person in cm
    weight : weight of the person in kg

    return body_surface_area in m**2
    """

    # For the record, surface of the body parts with no swimsuit (head 9%, hands:2x1%, feet:2x1.5%)
    # Formule de Shuter et Aslani
    return 0.00949 * (height**0.655) * (weight**0.441)


def show_foam_density(df):

    # df = get_data(raw=True)
    ts = r_nfoam * df["thickness_suit"] / 1000.0
    df["mass_suit_exp"] = ts

    # df["thickness_suit_estimation"] = r_nfoam * df["thickness_suit"] / 1000.0
    r_nfoam_corr = (df["mass_suit"].replace([0.0], [np.nan]) / ts).mean()
    print(f"Neoprene foam density is underestimated by a factor of {r_nfoam_corr:.2f}")
    print(f"{r_nfoam} kg/m3 => {r_nfoam_corr*r_nfoam:.0f} kg/m3. Calculation is done with {r_nfoam} kg/m3")

    df = df.sort_values("mass_suit_exp")

    fig, ax = plt.subplots(figsize=(15, 5))

    ax.set_title(f"Suit weight estimation from density (default is {r_nfoam:.0f} kg/m3)", fontsize=16)
    ax.plot(np.arange(2), np.arange(2), label=f"Weight estimation with density={r_nfoam:.0f} kg/m3", lw=6)
    ax.plot(
        np.arange(4),
        np.arange(4) / r_nfoam_corr,
        lw=6,
        label=f"Using {r_nfoam_corr*r_nfoam:.0f} kg/m3 instead of {r_nfoam} kg/m3",
    )
    ax.scatter(df["mass_suit"], df["mass_suit_exp"], s=60, label=f"Comparison with given data")

    fig.legend(loc=4, fontsize=16)


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
    for d in [".", "aplast/notebooks", "../aplast/notebooks", "aplast/aplast", "../aplast/aplast"]:
        if os.path.exists(f"{d}/{filename}"):
            return f"{d}/{filename}"
