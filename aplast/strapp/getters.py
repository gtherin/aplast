import streamlit as st

from trianer.core.labels import gl
import numpy as np
import streamlit as st
from streamlit_folium import folium_static

import trianer
from trianer import strapp

import trianer.strapp.inputs as tsti
from trianer.core.labels import gl, set_language


def get_pars(pars):
    return {"name" if k in ["race_format", "race_default"] else k: tsti.get_value(k) for k in pars}


def get_race():
    race_menu = tsti.get_value("race_menu")
    if race_menu == gl("existing_race"):
        race = trianer.Race(name=tsti.get_value("race_default"))
    elif race_menu == gl("existing_format"):
        pars = get_pars(["race_format", "cycling_dplus", "running_dplus"])
        race = trianer.Race(**pars)
    else:
        race = trianer.Race.init_from_cookies(tsti.get_value)
    return race


def get_temperature():
    race_menu = tsti.get_value("race_menu")
    if race_menu == gl("existing_race"):
        return tsti.get_temperature("race")
    elif race_menu == gl("existing_format"):
        return tsti.get_temperature("format")
    else:
        return tsti.get_temperature("perso")


def get_athlete():
    return trianer.Athlete(
        **get_pars(
            ["swimming_sX100m", "cycling_kmXh", "running_sXkm", "sudation", "vo2max"]
            + ["transition_swi2cyc_s", "transition_cyc2run_s", "weight_kg", "year_of_birth", "height_cm"]
        )
    )
