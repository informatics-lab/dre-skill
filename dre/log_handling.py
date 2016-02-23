from __future__ import division

import json
import math


def reduce_logs(logs):
    """
    Takes a list of log dictionaries and converts
    them into a minial form

    """

    # get a list of unique dictionaries (not including the forecast value)
    conditions = []
    for log in logs:
        conditions.append({k: v for k, v in log.items() if k is not "forecast"})
    unique_conditions = {json.dumps(log): log for log in logs}.values()
    
    reduced_logs = []
    for condition in unique_conditions:
        these_forecasts = []
        for log in logs:
            if all(item in log.items() for item in condition.items()):
                these_forecasts.append(log["forecast"])
        reduced_log = condition
        reduced_log["mean_forecast"] = sum(these_forecasts)/len(these_forecasts)
        reduced_log["min_forecast"] = min(these_forecasts)
        reduced_log["max_forecast"] = max(these_forecasts)
        reduced_log["n_forecasts"] = len(these_forecasts)

        reduced_logs.append(reduced_log)

    return reduced_logs