# I'm not sure what the best way to do this sort of thing is, but I think the
# most extensible will be to decouple the plotting from the backend data generation

# If I can do that, then all of the tasks will use the same plotting methods, which
# will be very nice

import pandas as pd

exercises = pd.read_csv("exercise.csv", names=["Date", "Exercise", "Value", "Number"])
with open("temp.txt", "w") as file:
    for name in exercises["Exercise"].unique():
        file.write(name + "\n")
