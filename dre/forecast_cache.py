class ForecastNotCachedException(Exception):
    """
    This exception is thown when the user tries to access
    forecast data which is considered not to be stored
    in the cache.

    Exception messesage details why the forecast was considered
    not to be cached.

    """
    def __init__(self, good_time, good_lat, good_lon, good_variable, time, loc, variable):
        message = ""
        if not good_time:
            message += "Time %s not found in any forecasts\n" % str(time)
        if not good_lat:
            message += "Latitude %d not found in any forecasts\n" % loc.lat
        if not good_lon:
            message += "Longitude %d not found in any forecasts\n" % loc.lon
        if not good_variable:
            message += "Variable %s not in any forecast" % variable
        super(ForecastNotCachedException, self).__init__(message)


class ForecastCache(object):
    """
    An object for persisting forecast data for a whole session.

    """
    def __init__(self):
        self.forecasts = []

    def cache_forecast(self, forecast, loc):
        """
        Args:
            * forecast (list): Forecast is a list of dictionaries
                where each dictionary element represents a
                a forecast for a specific point in time and space.
                At a minimum it must have a `date` element consisting
                of a `datetime.datetime` object.
            * loc (Loc): A location obejct which specifies the
                requested (as opposed to returned) location.

        """
        self.forecasts.append([forecast, loc])

    def get_forecast(self, time, loc, variable):
        """
        Gets the forecast data. First it attempts to retrieve
        suitable data from the cache, then from the data base
        e.g. data point, which is subsequently cached.

        Args:
            * time (datetime.datetime): time of desired forecast
            * loc (Loc): location of desired forecast
            * variable (string): name of desired forecast variable

        """
        good_forecast = []
        good_time = good_lat = good_lon = good_variable = False
        for forecast, forecast_loc in self.forecasts:
            this_good_time = this_good_lat = this_good_lon = this_good_variable = False 

            nearest_forecast = min(forecast, key=lambda v: abs(v.date-time))
            
            this_good_time = abs(nearest_forecast.date-time) < abs(forecast[0].date-forecast[1].date)
            good_time = True if this_good_time else good_time
            
            this_good_lat = forecast_loc.lat == loc.lat
            good_lat = True if this_good_lat else good_lat
            
            this_good_lon = forecast_loc.lon == loc.lon
            good_lat = True if this_good_lat else good_lat
            
            this_good_variable = variable in nearest_forecast.__dict__.keys()
            good_variable = True if this_good_variable else good_variable
            
            if this_good_time and this_good_lat and this_good_lon and this_good_variable:
                good_forecast.append(nearest_forecast)

        try:
            return min(good_forecast, key=lambda v: abs(v.date-time)).__dict__[variable].value
        except ValueError:
            raise ForecastNotCachedException(good_time, good_lat, good_lon, good_variable, time, loc, variable)