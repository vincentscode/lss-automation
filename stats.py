import datetime
import functools
import operator
from collections.abc import Iterable
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import math

missing_vehicles = [x.split("\t") for x in open("stats_missing_vehicle.tsv").read().split("\n")]
missing_vehicles = [{
    "date": datetime.datetime.fromisoformat(x[0]),
    "possible_vehicles": str(x[1])
} for x in missing_vehicles if len(x[0]) > 0]

max_days_ago = 1
hour_detail = True
def filter_missing(mv):
    mv_new = []
    today = datetime.datetime.today()
    for x in mv:
        days_ago = (today - x["date"]).days
        if days_ago <= max_days_ago:
            mv_new.append(x)

    return mv_new

repl = {
    "LF": "HLF 20",
    "LF 10": "HLF 20",
    "LF 20": "HLF 20",
    "TLF 4000": "HLF 20",
}

all_missing_combined = []
all_missing_combined_dated = {}
for x in filter_missing(missing_vehicles):
    v = x["possible_vehicles"]
    if "|" in v:
        v = v.split("|")[0]
    if v in repl:
        v = repl[v]

    all_missing_combined.append(v)

    if hour_detail:
        datekey = f'{x["date"].day}.{x["date"].month}.{x["date"].year} {x["date"].hour}'
    else:
        datekey = f'{x["date"].day}.{x["date"].month}.{x["date"].year}'

    if not datekey in all_missing_combined_dated:
        all_missing_combined_dated[datekey] = []
    all_missing_combined_dated[datekey].append(v)

all_missing_counts = dict(pd.value_counts(all_missing_combined))
all_missing_counts_dated = {}
for dk in all_missing_combined_dated:
    all_missing_counts_dated[dk] = dict(pd.value_counts(all_missing_combined_dated[dk]))

# print("Missing Vehicles")
# for v in all_missing_counts:
#     print("   ", v, "->", all_missing_counts[v])

fig, ax = plt.subplots()

## data
# detail data
plotdata = pd.DataFrame(all_missing_counts_dated)

# normalized average
x = [x for x in plotdata.index]
y = [all_missing_counts[x] / 24 for x in plotdata.index]

# normalized average error
dy = []
for i in plotdata.index:
    vals = []
    for dk in list(all_missing_counts_dated.keys()):
        if not i in all_missing_counts_dated[dk]:
            continue
        
        v = all_missing_counts_dated[dk][i]
        vals.append(v)

    vals = sorted(vals)

    cut_count = max([math.floor(len(vals) / 4), 1])
    top_cut = len(vals)-cut_count
    bottom_cut = cut_count
    v_top = vals[top_cut:]
    v_bottom = vals[:bottom_cut]
    v_top_avg = round(sum(v_top) / len(v_top), 2)
    v_bottom_avg = round(sum(v_bottom) / len(v_bottom), 2)

    diff = abs(v_top_avg - v_bottom_avg) / 2.0
    dy.append(diff)

    # print(i)
    # print(" >", len(vals), "=>", f"T: {top_cut}: | B: :{bottom_cut}")
    # print(" >", "Cuts:", f"T: {v_top} | B: {v_bottom}")
    # print(" >", "Avgs:", f"T: {v_top_avg} | B: {v_bottom_avg}")
    # print(" > >", "Diff:", diff)

## plot
total_bar_width = .9
b = ax.bar(x, y, color="black", width=total_bar_width)
p = plotdata.plot(kind="bar", ax=ax, width=total_bar_width)
e = ax.errorbar(x, y, yerr=dy, fmt="none", ecolor="gray", capsize=6, elinewidth=1, markeredgewidth=1)


## show
plt.show()
plt.savefig("stats.png")
