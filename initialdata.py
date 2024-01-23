# This won't be as standardized across datasets
import sqlalchemy
import pandas as pd
from datetime import strptime

# TODO: decouple the initial table setup from the mechanisms for inserting data

engine = sqlalchemy.create_engine("sqlite:///Exercises.db")


# TODO: try to maintain signature of inner function
def execute_stmt(func):
    def inner(conn, *args, **kwargs):
        stmt = func(*args, **kwargs)
        result = conn.execute(stmt)
        conn.commit()
        return result

    return inner


def value_stmt(value_type):
    return sqlalchemy.insert("ValueTypes").values(Name=value_type)


def unit_stmt(unit_name):
    return sqlalchemy.insert("Units").values(Name=unit_name)


def exercise_stmt(name, value_name, body_weight, per_side, assisted):
    return sqlalchemy.insert("Exercises").values(
        Name=name,
        WeightPerSideInd=per_side,
        BodyWeightInd=body_weight,
        WeightAssistedInd=assisted,
        ValueTypeId=value_types[value_name],
    )


def workout_stmt(dt):
    return sqlalchemy.insert("Workouts").values(Date=dt)


def set_stmt(workout_id, reps, value, unit_name, exercise_name):
    return sqlalchemy.insert("ExerciseSets").values(
        WorkoutId=workout_id,
        Reps=reps,
        Weight=value,
        UnitId=unit_ids[unit_name],
        ExerciseId=exercise_ids[exercise_name],
    )


def metric_stmt(name):
    return sqlalchemy.insert("Metrics").values(Name=name)


def measurement_stmt(dt, metric):
    return sqlalchemy.insert("Measurements").values(
        Date=dt, Value=value, MetricId=metric_ids[metric]
    )


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


###################### foundational basic data #######################

# it's a hair ridiculous to add maps to go back from names to ids.
# If names are supposed to be unique, they might as well be the pk
# I think this will be less of an issue later, where stuff is inputted with a GUI
unit_ids = {}
value_ids = {}
metric_ids = {}

value_types = ["weight", "time", "repetitions"]
units = ["lb", "kg", "s", "step", "rep"]
metrics = ["body weight"]
with engine.connect() as conn:
    for value in value_types:
        value_ids[value] = add_value(value).inserted_primary_key

    for unit in units:
        unit_ids[unit] = add_unit(unit).inserted_primary_key

    for metric in metrics:
        metric_ids[metric] = add_metric(metric).inserted_primary_key

######################### more advanced data ######################

exercise_info_df = pd.read_csv(
    "src/exercise info.csv",
    names=["Exercise", "value type", "per side", "bodyweight", "assisted"],
)

workout_df = pd.read_csv(
    "src/initialdata.csv", names=["Date", "exercise name", "value", "reps"]
)

# again, this is only the way it is because the input options are currently decoupled from the saved exercises
exercise_ids = {}
with engine.connect() as conn:
    for _, (
        name,
        value_type,
        per_side_ind,
        bodyweight_ind,
        assisted_ind,
    ) in exercise_info_df.iterrows():
        id = add_exercise(
            name, value_type, bodyweight_ind, per_side_ind, assisted_ind
        ).inserted_primary_key
        exercise_ids[name] = id

    for _, (date, exercise_name, value, reps) in workout_df.iterrows():
        pass
