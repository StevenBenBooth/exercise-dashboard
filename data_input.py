# This won't be as standardized across datasets
from sqlalchemy.ext.automap import automap_base
import sqlalchemy as sa
import pandas as pd
from datetime import datetime

engine = sa.create_engine("sqlite:///src/exercises.db")

# TODO: refactor so that sql definitions are taken care of by sqlalchemy
# Also, refactor to enable bulk inserts for simplicity

# TODO: reflection will be deprecated. Future-proof this
Base = automap_base()
Base.prepare(engine, reflect=True)

ValueTypes, Units, Exercises, Workouts, ExerciseSets, Metrics, Measurements = (
    Base.classes.ValueType,
    Base.classes.Units,
    Base.classes.Exercises,
    Base.classes.Workouts,
    Base.classes.ExerciseSets,
    Base.classes.Metrics,
    Base.classes.Measurements,
)
session = sa.orm.Session(engine)


# TODO: try to maintain signature of inner function
def execute_stmt(func):
    def inner(conn, *args, **kwargs):
        stmt = func(*args, **kwargs)
        result = conn.execute(stmt)
        conn.commit()
        return result

    return inner


def value_stmt(value_type):
    return sa.insert(ValueTypes).values(Name=value_type)


def unit_stmt(unit_name):
    return sa.insert(Units).values(Name=unit_name)


def exercise_stmt(name, value_id, body_weight, per_side, assisted):
    return sa.insert(Exercises).values(
        Name=name,
        WeightPerSideInd=per_side,
        BodyWeightInd=body_weight,
        WeightAssistedInd=assisted,
        ValueTypeId=value_id,
    )


def workout_stmt(dt, format="%m/%d/%Y"):
    """If passing in a string, format must be correctly specified"""
    try:
        dt = datetime.strptime(dt, format)
    except TypeError:
        pass
    # throws a ValueError if the format doesn't match
    return sa.insert(Workouts).values(Date=dt)


def set_stmt(workout_id, exercise_id, reps, value, unit_id):
    return sa.insert(ExerciseSets).values(
        WorkoutId=workout_id,
        Reps=reps,
        Weight=value,
        UnitId=unit_id,
        ExerciseId=exercise_id,
    )


def metric_stmt(name):
    return sa.insert(Metrics).values(Name=name)


def measurement_stmt(dt, metric_id, value):
    """If passing in a string, format must be correctly specified"""
    try:
        dt = datetime.strptime(dt, format)
    except TypeError:
        pass
    return sa.insert(Measurements).values(Date=dt, Value=value, MetricId=metric_id)


def muscle_stmt():
    raise NotImplementedError("Muscle stuff not supported!")


def muscle_group_stmt():
    raise NotImplementedError("Muscle stuff not supported!")


def mg_map_stmt():
    raise NotImplementedError("Muscle stuff not supported!")


def me_map_stmt():
    raise NotImplementedError("Muscle stuff not supported!")


add_value = execute_stmt(value_stmt)
add_unit = execute_stmt(unit_stmt)
add_exercise = execute_stmt(exercise_stmt)
add_workout = execute_stmt(workout_stmt)
add_set = execute_stmt(set_stmt)
add_metric = execute_stmt(metric_stmt)
add_measurement = execute_stmt(measurement_stmt)

############################ Silly key stuff ################################

# TODO: Because I implemented synthetic instead of natural keys, but inputting data is done with the natural keys,
# I need to convert these natural keys to the synthetic key they represent. It's a bit silly, but later when I
# update the data input method it won't be a huge deal


def get_synthetic_keymaps(conn, db_names):
    """Returns mappings from the names of units, values, metrics, and exercises to their corresponding syntehtic key.
    Note that this is a bit ridiculous, given it supposes that the names are natural keys
    """
    if not (isinstance(db_names, list) or isinstance(db_names, tuple)):
        db_names = [db_names]
    statements = map(lambda name: sa.text(f"select id, Name from {name}"), db_names)
    dfs = map(lambda s: pd.read_sql(s, conn), statements)
    maps = map(lambda df: df.set_index("Name").to_dict("index"), dfs)
    result_maps = list(map(lambda d: {k: v["id"] for k, v in d.items()}, maps))
    if len(result_maps) == 1:
        return result_maps[0]
    return result_maps


def create_workout(date, data_dict):
    with engine.connect() as conn:
        unit_ids, exercise_ids = get_synthetic_keymaps(conn, ["Units", "Exercises"])
        workout_id = add_workout(conn, date).inserted_primary_key[0]

        for entry in data_dict:
            add_set(
                conn,
                workout_id,
                exercise_ids[entry["exercise name"]],
                entry["reps"],
                entry["value"],
                unit_ids["lb"],
            )
    # TODO: Figure out what the support is for sqlalchemy with compound primary keys (relevant once I start looking into muscle/group mappings)
