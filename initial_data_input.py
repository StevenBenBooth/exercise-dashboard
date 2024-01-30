from data_input import *

###################### foundational basic data #######################

# it's a hair ridiculous to add maps to go back from names to ids.
# If names are supposed to be unique, they might as well be the pk
# I think this will be less of an issue later, where stuff is inputted with a GUI


value_types = ["weight", "time", "repetitions"]
units = ["lb", "kg", "s", "step", "rep"]
metrics = ["body weight"]
with engine.connect() as conn:
    for value in value_types:
        add_value(conn, value)

    for unit in units:
        add_unit(conn, unit)

    for metric in metrics:
        add_metric(conn, metric)
    metric_ids = get_synthetic_keymaps(conn, "Metrics")
    add_measurement(conn, "09/01/2022", metric_ids["body weight"], 140)
    add_measurement(conn, "01/01/2024", metric_ids["body weight"], 139)

######################### more advanced d3ata ######################


exercise_info_df = pd.read_csv(
    "src/exercise info.csv",
    names=["Exercise", "value type", "per side", "bodyweight", "assisted"],
)
# again, this is only the way it is because the input options are currently decoupled from the saved exercises
with engine.connect() as conn:
    unit_ids, value_ids, metric_ids = get_synthetic_keymaps(
        conn, ["Units", "ValueType", "Metrics"]
    )

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


workout_df = pd.read_csv(
    "src/initialdata.csv", names=["Date", "exercise name", "value", "reps"]
)

# we need to group by date (since I have only been doing one workout per day)
# then, I'll add a workout for each day, save the workout id, and use that to fill out
# the exercise sets associated with that id
with engine.connect() as conn:
    exercise_ids = get_synthetic_keymaps(conn, ["Exercises"])

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
