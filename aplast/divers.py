import pandas as pd

from .diver import *
from .constants import *


def get_data(surname=None, raw=False, clean=True, query=None):
    df = pd.read_csv(Diver.database_filename)

    df.columns = [
        "timestamp",
        "username",
        "name",
        "surname",
        "depth_max",
        "time_descent",
        "time_ascent",
        "depth_gliding_descent",
        "depth_gliding_descent_error",
        "depth_gliding_ascent",
        "depth_gliding_ascent_error",
        "volume_lungs",
        "mass_body",
        "mass_ballast",
        "thickness_suit",
        "mass_suit",
        "model_suit",
        "rights",
    ]

    df = df[
        [
            "surname",
            "depth_max",
            "time_descent",
            "time_ascent",
            "depth_gliding_descent",
            "depth_gliding_descent_error",
            "depth_gliding_ascent",
            "depth_gliding_ascent_error",
            "volume_lungs",
            "mass_body",
            "mass_ballast",
            "thickness_suit",
            "mass_suit",
        ]
    ]

    df = pd.concat(
        [
            df,
            pd.DataFrame.from_records(
                [
                    {
                        "surname": "Guillaume Néry",
                        "depth_max": 125,  # in m
                        "time_descent": 120,  # in sec
                        "time_ascent": 94,  # in sec
                        "depth_gliding_descent": 27.5,  # in m
                        "depth_gliding_descent_error": 2.5,  # in m
                        "depth_gliding_ascent": 7.5,  # in m
                        "depth_gliding_ascent_error": 2.5,  # in m
                        "volume_lungs": 9,  # in l
                        "mass_body": 78,  # in kg
                        "mass_ballast": 1,  # in kg
                        "thickness_suit": 1.5,  # in mm
                    }
                ]
            ),
        ]
    )
    df.index = range(len(df))

    if not raw:
        df["volume_lungs"] = df["volume_lungs"].clip(0, 10.0)
        df["depth_gliding_descent_error"].fillna(3.0, inplace=True)
        df["depth_gliding_ascent_error"].fillna(3.0, inplace=True)
        df["thickness_suit"].fillna(r_nfoam * df["thickness_suit"] / 1000.0, inplace=True)

        # Get suite volume in m3
        df["volume_suit"] = (surface_suit := 2) * df["thickness_suit"] / 1000.0
        df["speed_descent"] = df["depth_max"] / df["time_descent"]
        df["speed_ascent"] = df["depth_max"] / df["time_ascent"]
        df["volume_lungs"] = df["volume_lungs"] / 1000.0

        # Remove problematic data
        if clean:
            df = df[~df.surname.isin(["Lauper", "Carbone", "Sodde", "Underwater Photography & Media"])]

        if query:
            df = df.query(query)

    if surname is None:
        return df
    elif type(surname) == int:
        return Diver(df.iloc[surname].to_dict())

    return Diver(df.query(f"surname == '{surname}'").iloc[0].to_dict())


def minimize():
    df = get_data()

    df["volume_tissues"] = get_volume_tissues(
        df.mass_body,
        df.mass_ballast,
        df.volume_suit,
        df.volume_lungs,
        df.speed_descent,
        df.speed_ascent,
        df["depth_gliding_descent"],
        df["depth_gliding_ascent"],
    )
    df["drag_coefficient"] = get_drag_coefficient(
        df.volume_suit,
        df.volume_lungs,
        df.speed_descent,
        df.speed_ascent,
        df["depth_gliding_descent"],
        df["depth_gliding_ascent"],
    )

    minimization = [Diver(df.loc[i].to_dict()).minimize(verbose=False) for i in df.index]
    minimization = pd.DataFrame(minimization)

    df = df.merge(minimization, on="surname")
    return df
