import numpy as np
import datetime


class Variable:
    update_cookie = None
    cookies = {}

    def __init__(self, key=None, srange=None, help=None, label=None, default=None, orange=None) -> None:
        self.key, self.srange, self.help, self.label, self.default = key, srange, help, label, default
        self.orange = orange

    def get_format_value(self, var):
        if self.srange[0] == "t" and type(var) == str and ":" in var:
            dtimes = str(var).split(":")
            return datetime.time(int(dtimes[0]), int(dtimes[1]))
        elif self.srange[0] == "t" and type(var) in [str, int, str]:
            return datetime.time(int(var), 0)
        elif self.srange[0] == "f" and type(var) in [str, int]:
            return float(var)
        elif self.srange[0] == "i" and type(var) in [str, float, int]:
            return int(var)
        else:
            return var

    def get_init_value(self):
        var = Variable.cookies[self.key] if self.key in Variable.cookies else self.default
        return self.get_format_value(var)

    def get_input(self, input_cls):
        smin_value, smax_value, sstep = self.get_range_values()

        return input_cls(
            self.key if self.label is None else self.label,
            value=self.get_init_value(),
            min_value=smin_value,
            max_value=smax_value,
            step=sstep,
            key=self.key,
            help=self.help,
            on_change=lambda: Variable.update_cookie(self.key),
        )

    def get_range_values(self):
        stype, smin_value, smax_value, sstep = self.srange.split(":")
        if stype == "t":
            return (
                datetime.time(int(smin_value), 0),
                datetime.time(int(smax_value), 0),
                datetime.timedelta(minutes=int(sstep)),
            )
        elif stype == "i":
            return int(smin_value), int(smax_value), int(sstep)
        elif stype == "f":
            return float(smin_value), float(smax_value), float(sstep)


variables = {
    v["key"]: Variable(**v)
    for v in [
        dict(
            key="time_descent",
            srange="t:1:5:5",
            help="Time to reach the maximum depth from the surface (in seconds)",
            default=datetime.time(3, 0),
        ),
        dict(
            key="depth_max",
            srange="i:40:130:1",
            help="Maximal depth of the immersion (in meters)",
            default=100,
            # orange="r:0.8:1.2:10",  # in relative value, should multiply by current maxdepth
        ),
        dict(
            key="time_ascent",
            srange="t:1:5:5",
            help="Time to reach the surface from the maximum depth (in seconds)",
            default=datetime.time(3, 0),
        ),
        dict(
            key="depth_gliding_descent",
            srange="i:2:30:1",
            help="Depth at which you stop swimming and glide down (in meters)",
            default=20,
        ),
        dict(
            key="depth_gliding_descent_error",
            srange="i:1:10:1",
            help="Uncertainty of the above value (in meters)",
            default=5,
            label="error",
        ),
        dict(
            key="depth_gliding_ascent",
            srange="i:2:30:1",
            help="Depth at which you stop swimming and glide to the surface (in meters)",
            default=10,
        ),
        dict(
            key="depth_gliding_ascent_error",
            srange="i:1:10:1",
            help="Uncertainty of the above value (in meters)",
            default=5,
            label="error",
        ),
        dict(
            key="volume_lungs",
            srange="i:1:10:1",
            help="Total volume of your lungs: vital capacity + residual volume (in liters)",
            default=6,
            orange="a:0:10:20",  # in absolute value
        ),
        dict(key="mass_body", srange="i:40:120:1", help="Your weight (in kg)", default=70),
        dict(
            key="mass_ballast",
            srange="f:0:5:0.5",
            help="The weight of your ballast (in kg)",
            default=1,
            orange="a:0:5:20",  # in absolute value
        ),
        dict(key="thickness_suit", srange="f:0.:5.:0.2", help="The thickness of your suit (in mm)", default=1.5),
        dict(key="mass_suit", srange="f:0.:3.0:0.2", help="The weight of your suit (in kg)", default=1),
    ]
}

"""
        elif variable == "speed_factor":
            speed_factors = (index := np.linspace(0.8, 1.2, 10))
        elif variable == "Rt":
            volume_tissues = (mass_total / r_water) * (index := np.linspace(0.8, 1.2, 10))
"""


def get_var_slider(key):
    import streamlit as st

    return variables[key].get_input(st.slider)


def get_var_number(key):
    import streamlit as st

    return variables[key].get_input(st.number_input)


def set_var_on_change_function(update_cookie):
    Variable.update_cookie = update_cookie


def set_var_cookies(cookies):
    Variable.cookies = cookies
