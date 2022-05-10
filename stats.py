from pymongo import MongoClient
import datetime
import functools
import operator
from collections.abc import Iterable
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

register_matplotlib_converters()

client = MongoClient("localhost:27017")
db = client.lss_stats

# missions
missions = [x for x in db.missions.find({})]


# vehicles
missing_vehicles = [x for x in db.missing_vehicles.find({})]

def filter_missing(mv):
    return [x for x in mv if x["date"].day == datetime.datetime.today().day]

all_missing_combined = []
for v in filter_missing(missing_vehicles):
    any_list = False
    for itm in v["possible_vehicles"]:
        if not type(itm) == str and isinstance(itm, Iterable):
            any_list = True

    if any_list:
        flattened = functools.reduce(operator.iconcat, v["possible_vehicles"], [])
    else:
        flattened = v["possible_vehicles"]
    all_missing_combined += flattened

all_missing_counts = dict(pd.value_counts(all_missing_combined))

print("Missing Vehicles")
for v in all_missing_counts:
    print("   ", v, "->", all_missing_counts[v])

# credits
current_credits = [x for x in db.current_credits.find({})]
dates = [x["date"] for x in current_credits]
credits = [int(x["credits"]) for x in current_credits]

plt.plot_date(dates, credits, 'b-', label="credits")
plt.xlabel("time")
plt.ylabel("credits")
plt.legend()
plt.xticks(rotation=45)
plt.grid(color='gray', linestyle='dashed')
plt.show()
