from datetime import datetime
import pandas as pd
import numpy as np
import scipy as sp

from scipy import ndimage

import uncertainties as unc

from scipy.optimize import minimize

from .constants import *


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

    speed2 = speed_a**2 + speed_d**2
    pressure_eq_d = pressure_0 + depth_eq_d * g * r_water
    pressure_eq_a = pressure_0 + depth_eq_a * g * r_water
    press_speed2_d = pressure_eq_d * speed_d**2
    press_speed2_a = pressure_eq_a * speed_a**2
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

    speed2 = speed_a**2 + speed_d**2
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

    force_weight = g * (mass_body + mass_ballast + r_nfoam * volume_suit)
    force_archimede1 = g * r_water * (mass_ballast / r_ballast + (r_nfoam * volume_suit) / r_neo + volume_incompress)
    force_archimede2 = g * r_water * (volume_gas + (1 - r_nfoam / r_neo) * volume_suit)

    if force_weight <= 0:
        print(f"{surname} force_weight {force_weight} is negative")

    if force_archimede1 <= 0:
        print(f"{surname} force_archimede1 {force_archimede1} is negative")

    if force_archimede2 <= 0:
        print(f"{surname} force_archimede2 {force_archimede2} is negative")

    force_drag_descent = drag_coefficient * speed_descent**2
    force_drag_ascent = drag_coefficient * speed_ascent**2

    if force_drag_descent <= 0:
        print(f"{surname} force_drag_descent {force_drag_descent} is negative")

    if force_drag_ascent <= 0:
        print(f"{surname} force_drag_ascent {force_drag_ascent} is negative")

    force_descent = force_drag_descent - force_weight + force_archimede1
    force_ascent = force_drag_ascent + force_weight - force_archimede1

    pressure_depth_max = pressure_0 + depth_max * g * r_water

    def robust_log(value):
        if "uncertain" in str(type(value)):
            er = np.abs(value.std_dev / value.nominal_value)
            return unc.ufloat(np.log(value.nominal_value), er)
        return np.log(value)

    if force_descent >= 0:
        print(
            f"{surname} force_descent should be negative.\nOtherwise, it means that diver is not going deep enough to get out the gliding zone.",
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
    work_core += -force_archimede2 * robust_log(pressure_depth_max / pressure_0)
    work_core += force_archimede2 * robust_log(force_archimede2 / force_ascent)
    work_core += force_archimede2 * robust_log(-force_archimede2 / force_descent)

    work = depth_max * force_ascent + pressure_0 * work_core / (g * r_water)

    return work


class Diver:
    def get_speed(self, phase):
        if f"speed_{phase}" in self.data:
            return self.data[f"speed_{phase}"]

        return self.data["depth_max"] / float(self.get_time(phase))

    def get_time(self, phase):
        dtime = self.data[f"time_{phase}"]
        if type(dtime) in [float, int]:
            return int(dtime)

        times = str(dtime).split(":")
        return int(float(times[0]) * 60 + float(times[1]))

    def __init__(self, data: dict) -> None:

        self.data = data
        for c in [
            "surname",
            "depth_max",
            "mass_body",
            "mass_ballast",
            "thickness_suit",
            "volume_lungs",
        ]:
            setattr(self, c, data[c])

        self.time_descent = self.get_time("descent")
        self.time_ascent = self.get_time("ascent")

        self.speed_descent = self.get_speed("descent")
        self.speed_ascent = self.get_speed("ascent")

        self.depth_gliding_descent = unc.ufloat(
            self.data["depth_gliding_descent"], self.data["depth_gliding_descent_error"]
        )
        self.depth_gliding_ascent = unc.ufloat(
            self.data["depth_gliding_ascent"], self.data["depth_gliding_ascent_error"]
        )

        # Get suite volume in m3
        self.volume_suit = (
            data["volume_suit"] if "volume_suit" in data else (surface_suit := 2) * self.thickness_suit / 1000.0
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

        # Drag constant estimation
        self.drag_coefficient = get_drag_coefficient(
            self.volume_suit,
            self.volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            self.depth_gliding_descent,
            self.depth_gliding_ascent,
        )

        # Descent work estimation
        self.total_work = get_total_work(
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

    def minimize(self, method=None, verbose=True) -> None:

        # Function to minimize with respect to the user characteristics
        # mb and Tsmm variables to minimize
        # The different versions are used to estimate the uncertainty
        def f(param):
            mb, ts = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                ts / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fplusVt(param):
            mb, ts = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n + self.volume_tissues.s,
                ts / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fminusVt(param):
            mb, ts = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n - self.volume_tissues.s,
                ts / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n,
            )

        def fplusC(param):
            mb, ts = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                ts / 1000 * 2,
                self.volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                self.drag_coefficient.n + self.drag_coefficient.s,
            )

        def fminusC(param):
            mb, ts = param
            return get_total_work(
                self.surname,
                self.depth_max,
                self.mass_body,
                mb,
                self.volume_tissues.n,
                ts / 1000 * 2,
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

        thickness_suit_best = res.x[1]
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

        gain = work_proposal / self.total_work.n - 1

        if verbose:
            print(f"Best ballast weight \t\t= {mass_ballast_best} kg")
            print(f"Average optimal ballast weight \t= {mass_ballast_proposal} kg")
            print(f"Best suite thickness \t\t= {thickness_suit_best} mm")
            print(f"Average optimal suite thickness \t= {thickness_suit_proposal} mm\n")
            print(f"Performance gain = {gain * 100} %")

        return {
            "surname": self.surname,
            "work": self.total_work.n,
            "work_best": work_proposal.n,
            "mass_ballast_best": mass_ballast_best,
            "mass_ballast_proposal": mass_ballast_proposal,
            "thickness_suit_best": thickness_suit_best,
            "thickness_suit_proposal": thickness_suit_proposal,
            "gain": gain * 100,
        }

    def get_total_work(self, variable=None):

        volume_lungs = [self.volume_lungs]
        mass_ballast = [self.mass_ballast]
        depth_max = [self.depth_max]
        speed_factors = [1.0]
        volume_tissues = [self.volume_tissues.n]

        mass_total = self.mass_body + self.mass_ballast + r_nfoam * self.volume_suit

        if variable == "mass_ballast":
            mass_ballast = (index := np.linspace(0, 5, 20))
        elif variable == "depth_max":
            depth_max = (index := np.linspace(0.8, 1.2, 10) * self.depth_max)
        elif variable == "speed_factor":
            speed_factors = (index := np.linspace(0.8, 1.2, 10))
        elif variable == "Rt":
            volume_tissues = (mass_total / r_water) * (index := np.linspace(0.8, 1.2, 10))
        elif variable == "volume_lungs":
            volume_lungs = (index := np.linspace(0, 10, 20))
        else:
            index = None

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

        if index is None:
            return total_work

        return pd.Series(total_work, index=index)
