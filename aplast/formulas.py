import numpy as np
import matplotlib.pyplot as plt
import datetime

from . import constants


def get_body_surface_area(height_in_cm: float, weight_in_kg: float) -> float:
    """
    height_in_cm : height of the person in cm
    weight_in_kg : weight of the person in kg

    return body_surface_area in m**2
    """

    # For the record, surface of the body parts with no swimsuit (head 9%, hands:2x1%, feet:2x1.5%)
    # Formule de Shuter et Aslani
    return 0.00949 * (height_in_cm**0.655) * (weight_in_kg**0.441)


def get_total_lungs_capacity(height_in_cm: float, is_woman: bool=True) -> float:
    """
    height_in_cm : height of the person in cm
    is_woman : a boolean (by default, set to True)

    return total_lungs_capacity in liters
    """

    # Source: Bibliographie/Normes ERS 93.pdf, P.H. QUANJER, G.J. TAMMELING, J.E. COTES, O.F. PEDERSEN, R. PESLIN, J.C. YERNAULT, Lung volumes and forced ventilatory flows., Eur Resp J 1993;6 suppl 16:15-40
    slope_h, intercept =  (6.60, -5.79) if is_woman else (7.99, -7.08)

    # The factor converts cm to meters
    return slope_h * height_in_cm / 100. + intercept


def get_residual_volume(height_in_cm: float, year_of_birth: int, is_woman: bool= True) -> float:
    """
    height_in_cm : height of the person in cm
    year_of_birth : the year as 4-digits number
    is_woman : a boolean (by default, set to True)

    return residual_volume in liters
    """

    # Source: Bibliographie/Normes ERS 93.pdf, P.H. QUANJER, G.J. TAMMELING, J.E. COTES, O.F. PEDERSEN, R. PESLIN, J.C. YERNAULT, Lung volumes and forced ventilatory flows., Eur Resp J 1993;6 suppl 16:15-40
    slope_h, slope_a, intercept =  (1.31, 0.022, -1.23) if is_woman else (1.81, 0.016, -2.0)

    # Calculate age with a year uncertainty
    age = datetime.date.today().year - year_of_birth

    # The factor converts cm to meters
    return slope_h * height_in_cm / 100. + slope_a * age + intercept


def show_foam_density(df):

    ts = constants.r_nfoam * df["thickness_suit"] / 1000.0
    df["mass_suit_exp"] = ts

    # df["thickness_suit_estimation"] = r_nfoam * df["thickness_suit"] / 1000.0
    r_nfoam_corr = (df["mass_suit"].replace([0.0], [np.nan]) / ts).mean()
    print(f"Neoprene foam density is underestimated by a factor of {r_nfoam_corr:.2f}")
    print(f"{constants.r_nfoam} kg/m3 => {r_nfoam_corr*constants.r_nfoam:.0f} kg/m3. Calculation is done with {constants.r_nfoam} kg/m3")

    df = df.sort_values("mass_suit_exp")

    fig, ax = plt.subplots(figsize=(15, 5))

    ax.set_title(f"Suit weight estimation from density (default is {constants.r_nfoam:.0f} kg/m3)", fontsize=16)
    ax.plot(np.arange(2), np.arange(2), label=f"Weight estimation with density={constants.r_nfoam:.0f} kg/m3", lw=6)
    ax.plot(
        np.arange(4),
        np.arange(4) / r_nfoam_corr,
        lw=6,
        label=f"Using {r_nfoam_corr*constants.r_nfoam:.0f} kg/m3 instead of {constants.r_nfoam} kg/m3",
    )
    ax.scatter(df["mass_suit"], df["mass_suit_exp"], s=60, label=f"Comparison with given data")

    fig.legend(loc=4, fontsize=16)

