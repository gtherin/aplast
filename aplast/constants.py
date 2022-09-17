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
    return 0.00949 * (height ** 0.655) * (weight ** 0.441)
