import datetime
import functools
import operator
from collections.abc import Iterable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from pandas.plotting import register_matplotlib_converters
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--max-days-ago', type=float, default=4.0)
args = parser.parse_args()

register_matplotlib_converters()

max_days_ago = args.max_days_ago

data = [x.split("\t") for x in open("stats_credits.tsv").read().split("\n")]
today = datetime.datetime.today()

new_data = []
for x in data:
    if len(x[0]) > 0:
        k = datetime.datetime.fromisoformat(x[0])

        time_ago = (today - k)
        days_ago = time_ago.days + (time_ago.seconds / 86400)
        # print(time_ago.days, "=>", days_ago)
        if days_ago > max_days_ago:
            continue

        new_data.append(x)

data = new_data

credits = {}
credits_no_out = {}

offset = 0
last_v = 0
idx = 0
for x in data:
    k = datetime.datetime.fromisoformat(x[0])
    v = int(x[1])

    try:
        if last_v > v and last_v > int(data[idx+1][1]): # "next_v"
            spent = v - last_v
            offset += -spent
            # print("spent", -spent)
            # print("offset", offset)
    except:
        pass
    credits[k] = v
    credits_no_out[k] = v + offset

    last_v = v
    idx += 1


# data
x = list(credits.keys())
y = list(credits.values())
yn = list(credits_no_out.values())

# trendline
dates.set_epoch(x[0])
x_t = [dates.date2num(d) for d in x]

def best_fit(X, Y):
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    # print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b

a, b = best_fit(x_t, yn)
yfit = [a + b * xi for xi in x_t]
print('{:,.0f}'.format(round(b)), "credits per day")
print('{:,.0f}'.format(round(b / 24)), "credits per hour")

# plot
plt.plot(x, yn, label="Credits total")
plt.plot(x, y, label="Credits")
plt.plot(x, yfit, label="Trend")

# show
plt.ticklabel_format(style='plain', axis='y', useOffset=True)
plt.gca().set_ylim([0, None])
current_yticks = plt.gca().get_yticks()
plt.gca().set_yticks(current_yticks)
plt.gca().set_yticklabels(['{:,.0f}'.format(y) for y in current_yticks])
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.show()
