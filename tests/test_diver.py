import numpy as np

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

    if np.abs(div.drag_coefficient.n - 12.453969801529535) > 1e-4:
        raise Exception(np.abs(div.drag_coefficient.n - 12.453969801529535))

    if np.abs(div.volume_tissues.n - 0.07261323492078334) > 1e-4:
        raise Exception(np.abs(div.volume_tissues.n - 0.07261323492078334))

    if np.abs(div.total_work.n - 6137.868667295232) > 1e-4:
        raise Exception(np.abs(div.total_work.n - 6137.868667295232))

    print(div.get_total_work(variable=None))
