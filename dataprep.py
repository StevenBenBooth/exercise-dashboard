# I'm not sure what the best way to do this sort of thing is, but I think the
# most extensible will be to decouple the plotting from the backend data generation

# If I can do that, then all of the tasks will use the same plotting methods, which
# will be very nice
import pandas as pd
from calculators import calculate_orm, calculate_wilks_score
import sqlalchemy
from typing import Union, List
import numpy as np

engine = sqlalchemy.create_engine("sqlite:///src/exercises.db")


def get_exercise_series(exercise_id: int, agg_type="orm"):  # Union[List[int], int]
    # TODO: add support for plotting multiple exercises (if not here, then in plotting)

    # try:
    #     iter(exercise_ids)
    # except TypeError:
    #     exercise_ids = [exercise_ids]

    with engine.connect() as conn:
        matching_sets = pd.read_sql(
            sqlalchemy.text(
                f"""select ExerciseSets.id as id, Exercises.Name as exercise, Workouts.Date as date, Units.Name as unit, ExerciseSets.Reps as reps, ExerciseSets.Weight as weight
                from ExerciseSets 
                join Workouts on ExerciseSets.WorkoutId = Workouts.id 
                join Units on ExerciseSets.UnitId = Units.id
                join Exercises on Exercises.id = ExerciseSets.ExerciseId
                where Exercises.id = {exercise_id};"""
            ),
            conn,
            parse_dates=["date"],
        )
        matching_sets.set_index("id", inplace=True)

    # now we go through and merge each day into one event
    if agg_type == "orm":
        matching_sets["orm"] = calculate_orm(
            matching_sets["weight"], matching_sets["reps"]
        )
        res = matching_sets.groupby("date")["orm"].aggregate(np.max)
    elif agg_type == "volume":
        matching_sets["set volume"] = matching_sets["weight"] * matching_sets["reps"]
        res = matching_sets.groupby("date")["set volume"].aggregate(np.sum)
    else:
        raise NotImplementedError(
            "Currently only supports plotting orm and volume for exercises"
        )
    return list(res.index), res.to_list()


def get_powerlifting_series(agg_type=""):
    # first, pull lifts for the 3 exercises, and combine them into a "total lift" series
    if agg_type == "total":
        pass
    elif agg_type == "wilkes":
        # need to pull bodyweight
        pass
    else:
        raise NotImplementedError(
            "Currently only supports plotting totals and wilks score"
        )

print(get_exercise_series(1, agg_type="volume"))
