# This won't be as standardized across datasets
from sqlalchemy.ext.automap import automap_base
import sqlalchemy as sa
import pandas as pd
from datetime import datetime

# TODO: decouple the initial table setup from the mechanisms for inserting data

engine = sa.create_engine("sqlite:///src/exercises.db")

# TODO: refactor so that sql definitions are taken care of by sqlalchemy
# Also, refactor to enable bulk inserts for simplicity

# TODO: reflection will be deprecated
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


def workout_stmt(dt):
    return sa.insert(Workouts).values(Date=datetime.strptime(dt, "%m/%d/%Y"))


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
    return sa.insert(Measurements).values(
        Date=datetime.strptime(dt, "%m/%d/%Y"), Value=value, MetricId=metric_id
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
        value_ids[value] = add_value(conn, value).inserted_primary_key[0]

    for unit in units:
        unit_ids[unit] = add_unit(conn, unit).inserted_primary_key[0]

    for metric in metrics:
        metric_ids[metric] = add_metric(conn, metric).inserted_primary_key[0]

    add_measurement(conn, "09/01/2023", metric_ids["body weight"], 140)
######################### more advanced d3ata ######################

exercise_info_df = pd.read_csv(
    "src/exercise info.csv",
    names=["Exercise", "value type", "per side", "bodyweight", "assisted"],
)
# again, this is only the way it is because the input options are currently decoupled from the saved exercises
exercise_ids = {}
with engine.connect() as conn:
    for _, row in exercise_info_df.iterrows():
        name, value_type, per_side_ind, bodyweight_ind, assisted_ind = row
        id = add_exercise(
            conn,
            name,
            value_ids[value_type],
            bodyweight_ind,
            per_side_ind,
            assisted_ind,
        ).inserted_primary_key[0]
        exercise_ids[name] = id


workout_df = pd.read_csv(
    "src/initialdata.csv", names=["Date", "exercise name", "value", "reps"]
)

# we need to group by date (since I have only been doing one workout per day)
# then, I'll add a workout for each day, save the workout id, and use that to fill out
# the exercise sets associated with that id
with engine.connect() as conn:
    for date, data in workout_df.groupby(by="Date"):
        workout_id = add_workout(conn, date).inserted_primary_key[0]
        data.drop(columns=["Date"], inplace=True)
        data_dicts = data.to_dict("records")
        for d in data_dicts:
            add_set(
                conn,
                workout_id,
                exercise_ids[d["exercise name"]],
                d["reps"],
                d["value"],
                unit_ids["lb"],
            )
# TODO: Figure out what the support is for sqlalchemy with compound primary keys (relevant once I start looking into muscle/group mappings)
