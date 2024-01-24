from pint import UnitRegistry
import numpy as np

ureg = UnitRegistry()
Q_ = ureg.Quantity


# https://en.wikipedia.org/wiki/One-repetition_maximum#Estimating_1RM
def calculate_orm(weight, reps, style="brzycki"):
    """Computes the estimated one-rep maximum of an exercise based on a set"""
    if style == "brzycki":
        return np.divide(weight * 36, 37 - reps)
    elif style == "epley":
        return weight * (1 + reps / 30)
    raise ValueError(f"{style} one-rep max. formula is not implemented")


wilkes_coefficients = {
    "male": [
        47.46178854,
        8.472061379,
        0.07369410346,
        -0.001395833811,
        7.07665973070743e-6,
        -1.20804336482315e-8,
    ],
    "female": [
        -125.4255398,
        13.71219419,
        -0.03307250631,
        -0.001050400051,
        9.38773881462799e-6,
        -2.3334613884954e-8,
    ],
}


# https://en.wikipedia.org/wiki/Wilks_coefficient
# TODO: remove default sex value if released
def calculate_wilks_score(bw, lift, sex="male"):
    """Computes an athlete's Wilks score, using the 2020 formulation
    Returns the adjusted lift weight in the units it was inputted as"""
    try:
        a, b, c, d, e, f = wilkes_coefficients[sex]
    except KeyError:
        raise ValueError(
            "Currently, only male and female sexes are supported. I'm not sure if there are coefficients for intersex athletes."
        )
    # TODO: explicitly check that bw is a quantity
    original_units = bw.units
    bw = Q_(bw, "kg")
    lift = Q_(bw, "kg")

    coeff = 600 / (a + b * bw + c * bw**2 + d * bw**3 + e * bw**4 + f * bw**5)
    return Q_(coeff * lift, original_units)
