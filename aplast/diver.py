import pandas as pd
import numpy as np
import scipy as sp

from scipy import ndimage

import uncertainties as unc

# from uncertainties.umath import log
from scipy.optimize import minimize

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


# General constants
rho = 1025
rhob = 11000
rhon = 1230
rhonf = 170


def get_body_surface_area(height: float, weight: float) -> float:
    """
    height : height of the person in cm
    weight : weight of the person in kg

    return body_surface_area in m**2
    """

    # For the record, surface of the body parts with no swimsuit (head 9%, hands:2x1%, feet:2x1.5%)
    # Formule de Shuter et Aslani
    return 0.00949 * (height ** 0.655) * (weight ** 0.441)


def get_trajectory(time_descent, time_ascent, max_depth) -> pd.Series:
    x = np.arange(0, time_descent)
    y = -max_depth * np.arange(0, time_descent) / time_descent
    # y = -np.log10((np.cosh((x - 1) / 40) + 1))
    # y = max_depth * (y - y[0]) / np.abs(y[-1] - y[0])

    x2 = np.arange(0, time_ascent) + time_descent
    y2 = max_depth * np.arange(0, time_ascent) / time_ascent - max_depth

    x3 = np.append(x, x2)
    y3 = np.append(y, y2)
    return pd.Series(y3, index=x3)


def get_volume_tissues(mass_body, mass_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the volume occupied by tissue of the freediver body from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.

    mass_body    = mass of the body
    mass_ballast : mass of the ballast
    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = depth_gliding_descent +- error
    depth_eq_a   = depth_gliding_ascent +- error

    return tissues volume +- error
    """

    speed2 = speed_a ** 2 + speed_d ** 2
    pressure_eq_d = pressure_0 + depth_eq_d * g * r_water
    pressure_eq_a = pressure_0 + depth_eq_a * g * r_water
    press_speed2_d = pressure_eq_d * speed_d ** 2
    press_speed2_a = pressure_eq_a * speed_a ** 2
    ptot = pressure_eq_a * pressure_eq_d * r_neo * speed2

    def get_func(depth):
        return pressure_0 * r_neo * (r_water - r_nfoam) + depth * g * r_water * (r_water - r_neo) * r_nfoam

    Vt = (
        mass_ballast * (1 - r_water / r_ballast)
        - (
            -mass_body * ptot
            + pressure_0 * r_water * r_neo * (press_speed2_a + press_speed2_d) * volume_gas
            + (press_speed2_a * get_func(depth_eq_d) + press_speed2_d * get_func(depth_eq_a)) * volume_suit
        )
        / ptot
    ) / r_water
    return Vt


def get_drag_coefficient(volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the hydrodynamic drag coefficient (drag = C*speed**2) from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.

    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part) part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = depth_gliding_descent +- error
    depth_eq_a   = depth_gliding_ascent +- error

    """

    speed2 = speed_a ** 2 + speed_d ** 2
    mass_toid = r_neo * (volume_gas + volume_suit) - r_nfoam * volume_suit
    volume_toid = mass_toid / r_neo

    pressure_eq_d = pressure_0 + depth_eq_d * g * r_water
    pressure_eq_a = pressure_0 + depth_eq_a * g * r_water

    deltax_eq_a = pressure_eq_a / g / r_water
    deltax_eq_d = pressure_eq_d / g / r_water

    return (depth_eq_d - depth_eq_a) * pressure_0 * volume_toid / (deltax_eq_a * deltax_eq_d * speed2)


def get_total_work(
    surname,
    depth_max,
    mass_body,
    mass_ballast,
    volume_incompress,
    volume_suit,
    volume_gas,
    speed_descent,
    speed_ascent,
    drag_coefficient,
):
    """Calculation of the mechanical work spent for the descent

    depth_max   = depth_max
    mass_body    = mass of the body
    mass_ballast : mass of the ballast
    volume_incompress   = get_volume_tissues(mass_body, mass_ballast, volume_suit, volume_gas, speed_descent, speed_a, depth_eq_d, depth_eq_a) : volume of the incompressible (liquid and solid part) part of the body
    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descet speed : descent speed
    speed_a   = ascent speed : ascension speed
    drag_coefficient : hydrodynamic drag constant
    """

    force_weight = g * (mass_body + mass_ballast + rhonf * volume_suit)
    force_archimede1 = g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
    force_archimede2 = g * rho * (volume_gas + (1 - rhonf / rhon) * volume_suit)

    if force_weight <= 0:
        print(f"{surname} force_weight {force_weight} is negative")

    if force_archimede1 <= 0:
        print(f"{surname} force_archimede1 {force_archimede1} is negative")

    if force_archimede2 <= 0:
        print(f"{surname} force_archimede2 {force_archimede2} is negative")

    force_drag_descent = drag_coefficient * speed_descent ** 2
    force_drag_ascent = drag_coefficient * speed_ascent ** 2

    if force_drag_descent <= 0:
        print(f"{surname} force_drag_descent {force_drag_descent} is negative")

    if force_drag_ascent <= 0:
        print(f"{surname} force_drag_ascent {force_drag_ascent} is negative")

    force_descent = force_drag_descent - force_weight + force_archimede1
    force_ascent = force_drag_ascent + force_weight - force_archimede1

    pressure_depth_max = pressure_0 + depth_max * g * rho

    log_func = np.log if type(force_archimede2) == pd.Series else unc.umath.log

    if force_descent >= 0:
        print(
            f"{surname} force_descent should be negative",
            force_descent,
            "=",
            force_drag_descent,
            "-",
            force_weight,
            "+",
            force_archimede1,
            "; archimede2=",
            force_archimede2,
        )
        force_descent *= -1

    if force_ascent <= 0:
        print(
            f"{surname} force_ascent",
            force_archimede2,
            force_ascent,
            force_drag_ascent,
            force_weight,
            force_archimede1,
        )

    work_core = force_ascent - force_descent - 2 * force_archimede2
    work_core += -force_archimede2 * log_func(pressure_depth_max / pressure_0)
    work_core += force_archimede2 * log_func(force_archimede2 / force_ascent)
    work_core += force_archimede2 * log_func(-force_archimede2 / force_descent)

    work = depth_max * force_ascent + pressure_0 * work_core / (g * rho)

    return work


class Diver:
    def __init__(self, data: dict) -> None:
        self.data = data
        for c in ["surname", "depth_max", "speed_descent", "speed_ascent"]:
            setattr(self, c, data[c])
        for c in ["mass_body", "mass_ballast", "volume_suit", "volume_lungs"]:
            setattr(self, c, data[c])

        self.depth_gliding_descent = unc.ufloat(
            self.data["depth_gliding_descent"], self.data["depth_gliding_descent_error"]
        )
        self.depth_gliding_ascent = unc.ufloat(
            self.data["depth_gliding_ascent"], self.data["depth_gliding_ascent_error"]
        )

        # Tissue volume estimation
        self.volume_tissues = get_volume_tissues(
            self.mass_body,
            self.mass_ballast,
            self.volume_suit,
            self.volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            self.depth_gliding_descent,
            self.depth_gliding_ascent,
        )

        print(self.volume_lungs)
        print(self.volume_suit)
        print(self.volume_tissues.n)
        print(self.mass_body / r_water)

        # Drag constant estimation
        self.drag_coefficient = get_drag_coefficient(
            self.volume_suit,
            self.volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            self.depth_gliding_descent,
            self.depth_gliding_ascent,
        )

    def minimize(self, method=None, verbose=True) -> None:

        # Descent work estimation
        total_work = get_total_work(
            self.surname,
            self.depth_max,
            self.mass_body,
            self.mass_ballast,
            self.volume_tissues,
            self.volume_suit,
            self.volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            self.drag_coefficient,
        )

        # Function to minimize with respect to the user characteristics
        # mb and Tsmm variables to minimize
        # The different versions are used to estimate the uncertainty
        def f(param):
            mb, Tsmm = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                Tsmm / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fplusVt(param):
            mb, Tsmm = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n + self.volume_tissues.s,
                Tsmm / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fminusVt(param):
            mb, Tsmm = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n - self.volume_tissues.s,
                Tsmm / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fplusC(param):
            mb, Tsmm = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                Tsmm / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n + self.drag_coefficient.s,
            )

        def fminusC(param):
            mb, Tsmm = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                Tsmm / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n - self.drag_coefficient.s,
            )

        # Minimize with bounds
        # Parameters are mass_ballast, thickness_suit
        initial_guess = [1, 1.5]
        bounds = ((0, 5), (0, 10))
        # Working minimization L-BFGS-B, TNC, SLSQP
        res = minimize(f, initial_guess, bounds=bounds, method=method)
        resplusVt = minimize(fplusVt, initial_guess, bounds=bounds, method=method)
        resminusVt = minimize(fminusVt, initial_guess, bounds=bounds, method=method)
        resplusC = minimize(fplusC, initial_guess, bounds=bounds, method=method)
        resminusC = minimize(fminusC, initial_guess, bounds=bounds, method=method)

        mass_ballast_best = res.x[0]
        mb_plusVt = resplusVt.x[0]
        mb_minusVt = resminusVt.x[0]
        mb_plusC = resplusC.x[0]
        mb_minusC = resminusC.x[0]

        mass_ballast_mean = (mb_plusVt + mb_minusVt + mb_plusC + mb_minusC) / 4
        mass_ballast_err = np.sqrt((mass_ballast_mean - mb_plusVt) ** 2 + (mass_ballast_mean - mb_plusC) ** 2)
        mass_ballast_proposal = unc.ufloat(mass_ballast_mean, mass_ballast_err)

        Tsmm_best = res.x[1]
        Tsmm_plusVt = resplusVt.x[1]
        Tsmm_minusVt = resminusVt.x[1]
        Tsmm_plusC = resplusC.x[1]
        Tsmm_minusC = resminusC.x[1]

        Tsmm_mean = (Tsmm_plusVt + Tsmm_minusVt + Tsmm_plusC + Tsmm_minusC) / 4
        Tsmm_err = np.sqrt((Tsmm_mean - Tsmm_plusVt) ** 2 + (Tsmm_mean - Tsmm_plusC) ** 2)
        thickness_suit_proposal = unc.ufloat(Tsmm_mean, Tsmm_err)

        # Performance gain
        work_proposal = get_total_work(
            self.surname,
            self.depth_max,
            self.mass_body,
            mass_ballast_proposal,
            self.volume_tissues.n,
            thickness_suit_proposal / 1000 * 2,
            self.volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            self.drag_coefficient.n,
        )

        gain = work_proposal / total_work.n - 1

        if verbose:
            print(f"Best ballast weight \t\t= {mass_ballast_best} kg")
            print(f"Average optimal ballast weight \t= {mass_ballast_proposal} kg")
            print(f"Best suite thickness \t\t= {Tsmm_best} mm")
            print(f"Average optimal suite thickness \t= {thickness_suit_proposal} mm\n")
            print(f"Performance gain = {gain * 100} %")

        return {
            "surname": self.surname,
            "work": total_work.n,
            "mass_ballast_best": mass_ballast_best,
            "mass_ballast_proposal": mass_ballast_proposal,
            "thickness_suit_best": Tsmm_best,
            "thickness_suit_proposal": thickness_suit_proposal,
            "gain": gain * 100,
        }

    def get_total_work(self, variable="mass_ballast"):

        volume_lungs = [self.volume_lungs]
        mass_ballast = [self.mass_ballast]
        depth_max = [self.depth_max]
        speed_factors = [1.0]
        volume_tissues = [self.volume_tissues.n]

        mass_total = self.mass_body + self.mass_ballast + rhonf * self.volume_suit

        if variable == "mass_ballast":
            mass_ballast = (index := np.linspace(0, 5, 20))
        elif variable == "depth_max":
            depth_max = (index := np.linspace(0.8, 1.2, 10) * self.depth_max)
        elif variable == "speed_factor":
            speed_factors = (index := np.linspace(0.8, 1.2, 10))
        elif variable == "Rt":
            volume_tissues = (mass_total / r_water) * (index := np.linspace(0.8, 1.2, 10))
        else:
            volume_lungs = (index := np.linspace(0, 10, 20))

        total_work = [
            get_total_work(
                self.surname,
                dm,
                self.mass_body,
                mb,
                vt,
                self.volume_suit,
                l,
                self.speed_descent * sf,
                self.speed_ascent * sf,
                self.drag_coefficient,
            ).n
            for l in volume_lungs
            for mb in mass_ballast
            for dm in depth_max
            for sf in speed_factors
            for vt in volume_tissues
        ]

        return pd.Series(total_work, index=index)

    def show(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle
        from matplotlib.patheffects import withStroke
        from matplotlib.ticker import AutoMinorLocator, MultipleLocator

        print(self.data)

        royal_blue = [0, 20 / 256, 82 / 256]

        X = np.linspace(0.5, 3.5, 100)
        Y1 = 3 + np.cos(X)
        Y2 = 1 + np.cos(1 + X / 0.75) / 2
        Y3 = np.random.uniform(Y1, Y2, len(X))

        fig, ax = plt.subplots(figsize=(15, 5))

        ax.tick_params(which="major", width=1.0, length=10, labelsize=14)
        ax.tick_params(which="minor", width=1.0, length=5, labelsize=10, labelcolor="0.25")

        ax.grid(linestyle="--", linewidth=0.5, color=".25", zorder=-10)

        # ax.plot(X, Y1, c="C0", lw=2.5, label="Blue signal", zorder=10)

        max_depth = 125  # in m
        time_descent = 120  # in sec
        time_ascent = 94  # in sec

        track = get_trajectory(time_descent, time_ascent, max_depth)

        ydee = 27.5
        xdee = track[track + ydee < 0].index[0]

        yaee = 7.5
        xaee = track[track + yaee < 0].index[-1]

        track1 = np.ma.masked_where(track.index <= xdee, track)
        track2 = np.ma.masked_where((track.index > xdee) & (track.index < xaee), track)

        ax.plot(track.index, track1, track.index, track2, lw=2.5)

        ax.set_title(f"Position-time estimation of {self.surname}", fontsize=20, verticalalignment="bottom")
        ax.set_xlabel("Time in seconds", fontsize=14)
        ax.set_ylabel("Depth in meters", fontsize=14)

        def annotate(x, y, text):
            ax.add_artist(
                Circle(
                    (x, y),
                    radius=10.15,
                    clip_on=False,
                    linewidth=2.5,
                    edgecolor=royal_blue + [0.6],
                    facecolor="none",
                    path_effects=[withStroke(linewidth=7, foreground="white")],
                )
            )

            ax.text(
                x,
                y - 0.2,
                text,
                ha="center",
                va="top",
                weight="bold",
                color=royal_blue,
            )

        annotate(xdee, -ydee, "Equilibrium")
        annotate(xaee, -yaee, "Equilibrium")

        # newax = fig.add_axes([0.2, 0.2, 0.1, 0.1], anchor="NE")
        # newax.imshow(plt.imread("diver.png"))
        # newax.axis("off")

        newax = fig.add_axes([0.3, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread("diver.png"), 50))
        newax.axis("off")

        newax = fig.add_axes([0.6, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread("diver.png"), 130))
        newax.axis("off")

        plt.show()
