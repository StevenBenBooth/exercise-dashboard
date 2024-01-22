# This won't be as standardized across datasets
import sqlalchemy
import pandas as pd

engine = sqlalchemy.create_engine("sqlite:///Exercises.db")

# it's a hair ridiculous to add maps to go backwards. If names are supposed to be unique, they might as well be
# this will be less of an issue later, where stuff is inputted with a GUI
units_ids = {}


def add_unit(unit_name):
    return sqlalchemy.insert("Units").values(Name=unit_name)


def add_exercise(name, unit_name, body_weight, per_side, assisted):
    return sqlalchemy.insert("Exercises").values(
        Name=name,
        WeightPerSideInd=per_side,
        BodyWeightInd=body_weight,
        UnitId=units_ids[unit_name],
    )


units = ["lb", "kg", "s", "step", "rep"]

exercise_info_df = pd.read_csv(
    "src/exercise info.csv",
    names=["Exercise", "unit name", "per side", "bodyweight", "assisted"],
)


with engine.connect() as conn:
    for unit in units:
        result = conn.execute(add_unit(unit))
        conn.commit()
        units_ids[unit] = result.inserted_primary_key

    for exercise in []:
        pass
