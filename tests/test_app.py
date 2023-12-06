import numpy as np

import aplast
import aplast.diver


def test_get_volume_tissues():
    d = aplast.Diver(
        data={
            "surname": "No-one",
            "depth_max": 85.0,
            "time_descent": 100,
            "time_ascent": 100,
            "depth_gliding_descent": 28.0,
            "depth_gliding_descent_error": 3.0,
            "depth_gliding_ascent": 5.0,
            "depth_gliding_ascent_error": 3.0,
            "volume_lungs": 0.006,
            "mass_body": 55.0,
            "mass_ballast": 1.0,
            "thickness_suit": 1.5,
        }
    )
    solution = d.minimize()

    for k, v in solution.items():
        print(k, v)
