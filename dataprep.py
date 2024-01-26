import pandas as pd
from calculators import calculate_orm, calculate_wilks_score
import sqlalchemy
import numpy as np
import pint

engine = sqlalchemy.create_engine("sqlite:///src/exercises.db")


def query_bw(date):
    """Returns most recent bodyweight before `date`"""

    # Unfortunates, SQLite doesn't play so nice with dates, so I couldn't select in the query
    with engine.connect() as conn:
        df = pd.read_sql(
            sqlalchemy.text(
                f"""select Measurements.Date as dt, Measurements.Value as weight
                    from Measurements 
                    where Measurements.MetricId = 1"""
            ),
            conn,
        )
    dates = pd.to_datetime(df["dt"], format="%Y-%m-%d %H:%M:%S")
    dates = dates[dates < pd.to_datetime(date)]
    assert len(dates) > 0, f"No bodyweight recorded before {date}"
    return sorted(dates, reverse=True)[0]


def query_sets(exercise_id):
    # TODO: add support for plotting multiple exercises (if not here, then in plotting)
    # TODO: implement using support for units. There is a pint-pandas, but it seems to still be in development
    # try:
    #     iter(exercise_ids)
    # except TypeError:
    #     exercise_ids = [exercise_ids]

    with engine.connect() as conn:
        df = pd.read_sql(
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
        df.set_index("id", inplace=True)
    return df


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
    return list(res.index), list(res)


# TODO: refactor all of this to try to use dataframes for as long as possible. All the looping and casting is awkward and inefficient


def get_top_lift_series(exercise_id: int, window=30):
    """returns a series of the best ORMs for `exercise_id`, where each lift is valid for `window` days"""
    start_dates, orms = get_exercise_series(exercise_id)
    best_res = {}
    # TODO: This is heinously inefficient. Refactor
    for start_date, value in zip(start_dates, orms):
        for date in pd.date_range(
            start_date, start_date + pd.Timedelta(window, unit="D")
        ):
            try:
                best_res[date].append(value)
            except KeyError:
                best_res[date] = [value]
    # yucky
    return tuple(zip(*[(key, max(vals)) for key, vals in best_res.items()]))


def normalize_by_bw(exercise_series):
    # TODO: refactor with two pointer implementation for efficiency
    # directly returning bw dates would be much more efficient
    xs, ys = exercise_series

    # eww to performance and style
    return tuple(zip(*[(x, y / query_bw(x)) for x, y in zip(xs, ys)]))


def get_powerlifting_series(agg_type="", lift_window=30):
    """Lift window is how many days a set should count for when computing"""
    # first, pull lifts for the 3 exercises, and combine them into a "total lift" series
    # I'm going to generate the list, then pull the best lift over the past time period for the calculation
    lifts = [
        get_exercise_series(1),
        get_exercise_series(5),
        get_exercise_series(16),
    ]
    # series = [deadlifts, bench, squats]
    best_lifts = [get_top_lift_series(lift) for lift in lifts]

    if agg_type == "raw":
        return best_lifts

    if agg_type == "proportions":
        return [normalize_by_bw(series) for series in best_lifts]

    # if these were series, it could be more efficient.
    # TODO: make plotting handle series correctly, so it's not in the prep stage
    vals = {}
    for lst in best_lifts:
        for date, weight in zip(*lst):
            try:
                vals[date].append(weight)
            except KeyError:
                vals[date] = [weight]

    totals = [(date, sum(trio)) for date, trio in lst if len(trio) == 3]
    dates, tots = list(zip(*totals))
    if agg_type == "total":
        return dates, tots

    elif agg_type == "wilkes":
        pass
    else:
        raise NotImplementedError(
            "Currently only supports plotting totals, proportions, and wilkes score"
        )
