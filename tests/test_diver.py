import pandas as pd

import aplast
import aplast.diver


def test_get_volume_tissues():

    # data = aplast.divers.get_data(surname="Guillaume Néry", raw=False)
    data = aplast.divers.get_data()
    print(data)

    data["volume_tissues"] = aplast.diver.get_volume_tissues(
        data.mass_body,
        data.mass_ballast,
        data.volume_suit,
        data.volume_lungs,
        data.speed_descent,
        data.speed_ascent,
        data["depth_gliding_descent"],
        data["depth_gliding_ascent"],
    )
    data["drag_coefficient"] = aplast.diver.get_drag_coefficient(
        data.volume_suit,
        data.volume_lungs,
        data.speed_descent,
        data.speed_ascent,
        data["depth_gliding_descent"],
        data["depth_gliding_ascent"],
    )

    # Make test on drag_coefficient and volume_tissues
    div = aplast.Diver(data.query(f"surname =='Guillaume Néry'").T[23].to_dict())
    print(div.get_total_work(variable=None))
