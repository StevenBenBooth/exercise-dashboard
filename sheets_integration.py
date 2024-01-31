import gspread
import pandas as pd
import numpy as np
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from data_input import create_workout

GOOGLE_TZ = "US/Pacific"
MY_TZ = "US/Eastern"

# Based on https://www.twilio.com/en-us/blog/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python-html


def add_recent_data():
    # use creds to create a client to interact with the Google Drive API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "src/exercise-tracker-412701-9b453b6dc305.json", scope
    )
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Exercises").sheet1

    df = get_records(sheet)
    last_run = cache_time()
    # TODO: need to copy to avoid warning; is there a better way?
    valid_workouts = df[df["Timestamp"] > last_run].copy()
    print(f"Adding information for {len(valid_workouts)} sets")

    valid_workouts.drop(columns=["Timestamp"], inplace=True)
    valid_workouts.rename(
        columns={"exercise names": "exercise name", "weight": "value"}, inplace=True
    )

    for date, data in valid_workouts.groupby(by="Date"):
        data.drop(columns=["Date"], inplace=True)
        create_workout(date, data.to_dict(orient="records"))


# TODO: add time gap as a condition for splitting new input data into workouts


def get_records(sheet):
    """Converts the sheet info into a dataframe to be consumed"""
    # Extract and print all of the values
    records = sheet.get_all_records()

    # Google timestamps are in Pacific Time, so I have to convert them
    df = pd.DataFrame(records)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df[["Weight", "Reps", "Number of sets"]] = df[
        ["Weight", "Reps", "Number of sets"]
    ].apply(pd.to_numeric)
    df.set_index("Timestamp", inplace=True, drop=False)
    df.index = df.index.tz_localize(GOOGLE_TZ).tz_convert(MY_TZ)
    df.fillna({"Number of sets": 1}, inplace=True)
    # For some reason it uses floats for the sets column
    df["Number of sets"] = pd.to_numeric(df["Number of sets"], downcast="integer")
    new_df = pd.DataFrame(
        np.repeat(df.values, df["Number of sets"], axis=0),
        columns=["Timestamp", "exercise names", "weight", "reps", "Number of sets"],
    )
    new_df["Date"] = new_df["Timestamp"].map(lambda x: x.date())
    new_df.drop(columns=["Number of sets"], inplace=True)
    return new_df


def cache_time():
    """Returns a timezone-aware dt of the last time this was run, and caches the current time of this run"""
    with open("src\cache.txt", "r") as f:
        last_time = pd.Timestamp(f.readline()).to_datetime64()
    with open("src\cache.txt", "w") as f:
        current_time = datetime.now().astimezone()
        f.write(str(current_time))
    return last_time


add_recent_data()
