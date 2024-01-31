import pandas as pd
from calculators import calculate_orm, calculate_wilks_score
import sqlalchemy
import numpy as np

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
    df["dt"] = pd.to_datetime(df["dt"])
    df = df[df["dt"] < pd.to_datetime(date)]
    df.set_index("dt", inplace=True)
    assert len(df) > 0, f"No bodyweight recorded before {date}"
    df.sort_index(inplace=True)
    return list(df.tail(1).weight)[0]


def query_sets(exercise_id):
    # TODO: add support for plotting multiple exercises (if not here, then in plotting)
    # TODO: implement using support for units. There is a pint-pandas, but it seems to still be in development

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
    if agg_type == "orm":
        # TODO: don't do orm calculations or "bw prop" for exercises that don't actually use weight (e.g. plank)
        matching_sets["orm"] = calculate_orm(
            matching_sets["weight"], matching_sets["reps"]
        )
        res = matching_sets.groupby("date")["orm"].aggregate(np.max)
    elif agg_type == "volume":
        # TODO: double volume for exercises which are "per side"
        matching_sets["set volume"] = matching_sets["weight"] * matching_sets["reps"]
        res = matching_sets.groupby("date")["set volume"].aggregate(np.sum)
    else:
        raise NotImplementedError(
            "Currently only supports plotting orm and volume for exercises"
        )
    return list(res.index), list(res)


# TODO: refactor all of this to try to use dataframes for as long as possible. All the looping and casting is awkward and inefficient
# Putting all the awkward conversions into the other modules would streamline this


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
    best_res = {k: v for k, v in best_res.items() if k <= pd.to_datetime("now")}
    # yucky
    return list(zip(*[(key, max(vals)) for key, vals in best_res.items()]))


def normalize_by_bw(exercise_series):
    # TODO: refactor with two pointer implementation for efficiency
    # directly returning series of bw dates would be much more efficient
    xs, ys = exercise_series

    # eww to performance and style
    return list(zip(*[(x, y / query_bw(x)) for x, y in zip(xs, ys)]))


def get_powerlifting_series(agg_type="raw", lift_window=30):
    """Lift window is how many days a set should count for when computing"""
    # TODO: standardize output type

    # lift ids correspond to [deadlifts, bench, squats]
    # TODO: programmatically get ids for deadlift, bench, squat
    best_lifts = [get_top_lift_series(lift_id, lift_window) for lift_id in (1, 5, 16)]

    if agg_type == "raw":
        return best_lifts

    if agg_type == "proportions":
        return [normalize_by_bw(series) for series in best_lifts]

    vals = {}
    for lst in best_lifts:
        for date, weight in zip(*lst):
            try:
                vals[date].append(weight)
            except KeyError:
                vals[date] = [weight]

    totals = [(date, sum(trio)) for date, trio in vals.items() if len(trio) == 3]
    dates, tots = list(zip(*totals))
    if agg_type == "total":
        return dates, tots

    elif agg_type == "wilkes":
        return dates, [
            calculate_wilks_score(query_bw(date), lift)
            for date, lift in zip(dates, tots)
        ]

    raise NotImplementedError(f"Does not support {agg_type} for plotting")
