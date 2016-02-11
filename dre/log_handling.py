import numpy as np


def reduce_logs(logs):
    """
    Takes a list of log dictionaries and converts
    them into a minial form

    """

    # get a list of unique dictionaries (not including the forecast value)
    conditions = []
    for log in logs:
        conditions.append({k: v for k, v in log.items() if k is not "forecast"})
    unique_conditions = list(np.unique(np.array(conditions)))
    reduced_logs = []
    for condition in unique_conditions:
        these_forecasts = []
        for log in logs:
            if all(item in log.items() for item in condition.items()):
                these_forecasts.append(log["forecast"])
        reduced_log = condition
        reduced_log["mean_forecast"] = np.mean(these_forecasts)
        reduced_log["min_forecast"] = np.min(these_forecasts)
        reduced_log["max_forecast"] = np.max(these_forecasts)
        reduced_log["n_forecasts"] = len(these_forecasts)

        reduced_logs.append(reduced_log)

    return reduced_logs