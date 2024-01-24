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


def query_bw():
    """Returns most recent bodyweight"""
    raise NotImplementedError("Doesn't support Wilks yet.")


def query_sets(exercise_id):
    # TODO: add support for plotting multiple exercises (if not here, then in plotting)

    # try:
    #     iter(exercise_ids)
    # except TypeError:
    #     exercise_ids = [exercise_ids]

    with engine.connect() as conn:
        res = pd.read_sql(
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
        res.set_index("id", inplace=True)
    return res


def get_exercise_series(exercise_id: int, agg_type="orm"):  # Union[List[int], int]
    matching_sets = query_sets(exercise_id)

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


class EventDates:
    def __init__(self) -> None:
        self.dates = {}

    def add(self, date, eventId):
        try:
            self.dates[date].append(eventId)
        except KeyError:
            self.dates[date] = [eventId]

    def get_events(self, date):
        try:
            return self.dates[date]
        except KeyError:
            return []

    def date_bounds(self):
        sorted_dates = sorted(self.dates.keys())
        return sorted_dates[0], sorted_dates[-1]

    def __repr__(self) -> str:
        return f"{self.dates}\n"


def get_powerlifting_series(agg_type="", lift_window=1):
    """Lift window is how many months a set should count for when computing"""
    # first, pull lifts for the 3 exercises, and combine them into a "total lift" series
    # I'm going to generate the list, then pull the best lift over the past time period for the calculation
    series = [
        get_exercise_series(1),
        get_exercise_series(5),
        get_exercise_series(16),
    ]
    # series = [deadlifts, bench, squats]
    # maps dates to dictionaries containing valid large lifts for that date
    date_map = {}
    for xs, ys in series:
        pass
    # for plotting, pick the latest early date and earliest late date
    # or present, if earliest late date is in the future
    total_series = []
    if agg_type == "total":
        return total_series
    elif agg_type == "wilkes":
        pass
    else:
        raise NotImplementedError(
            "Currently only supports plotting totals and wilks score"
        )
