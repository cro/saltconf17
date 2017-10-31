# -*- Coding: utf-8 -*-
'''
Support for OpenWeatherMap Personal Weather Stations
'''

# Import Python libs
from __future__ import absolute_import
import logging
import json
import datetime
import calendar
import dateutil

# Import salt libs
from salt.exceptions import CommandExecutionError
import salt.utils.path
import pyowm.exceptions
from pyowm.stationsapi30 import measurement

log = logging.getLogger(__name__)


def __virtual__():
    if 'proxy' not in __opts__:
        return (False, 'This module only works with proxy minions.')
    return True


def send_measurement(temperature, wind_speed, dt=None):
    '''
    Send a measurement to OpenWeatherMap for this station.
    Currently the only measurements supported here are
    temperature (in degrees Celsius) and wind speed.
    '''
    station_id = __proxy__['pws.pwsid']()
    mgr = __proxy__['pws.sta']()

    if dt is None:
        now = datetime.datetime.now()
        dt = calendar.timegm(now.timetuple())
    else:
        stamp = dateutil.parser.parse(dt)
        dt = calendar.timegm(stamp.timetuple())

    meas = measurement.Measurement(station_id, dt,
                                   temperature=temperature, wind_speed=wind_speed)

    try:
        mgr.send_measurement(meas)
    except Exception as exc:
        return str(exc)

    return True


def get_measurements(start_time=None, end_time=None, granularity='m'):
    '''
    Get aggregated measurements from this station for a range.
    Granularity can be `m` for minutes, `h` for hours, or `d` for days.
    start and end times can be any time and date supported by the
    dateutil library parser.
    '''
    station_id = __proxy__['pws.pwsid']()
    mgr = __proxy__['pws.sta']()

    if start_time is None:
        start_stamp = datetime.datetime.now()
        start_dt = calendar.timegm(start_stamp.timetuple()) - (60*60*24)
    else:
        start_stamp = dateutil.parser.parse(start_time)
        start_dt = calendar.timegm(start_stamp.timetuple())

    if end_time is None:
        end_stamp = datetime.datetime.now()
        end_dt = calendar.timegm(end_stamp.timetuple())
    else:
        end_stamp = dateutil.parser.parse(end_time)
        end_dt = calendar.timegm(end_stamp.timetuple())

    measures = mgr.get_measurements(station_id, granularity, start_dt, end_dt, limit=20)

    ret = []
    for measure in measures:
        ret.append(measure.to_dict())

    return ret


def weather():
    '''
    Call the OpenWeatherMap API through a proxy minion.  Retrieve the current weather
    for the area around this personal weather station.
    '''

    lat = __proxy__['pws.station']().lat
    lon = __proxy__['pws.station']().lon
    weather_result = __proxy__['pws.api']().weather_at_coords(lat, lon)

    return json.loads(weather_result.to_JSON())
