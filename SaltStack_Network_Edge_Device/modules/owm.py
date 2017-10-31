
# -*- Coding: utf-8 -*-
'''
Support for OpenWeatherMap
'''

# Import Python libs
from __future__ import absolute_import
import logging
import json

# Import salt libs
from salt.exceptions import CommandExecutionError
import salt.utils.path
import pyowm.exceptions

log = logging.getLogger(__name__)


def __virtual__():
    if 'proxy' not in __opts__:
        return (False, 'This module only works with proxy minions.')
    return True


def weather(place=None):
    '''
    Call the OpenWeatherMap API through a proxy minion.  Return the JSON
    results for weather at a particular place.  Place can be a well-known
    geographic location like Salt Lake City, UT; Disneyland, USA; or 
    Washington, DC or a zipcode (84041).
    '''
    if not place:
        raise CommandExecutionError('owm.weather needs a place or a zipcode.')
    else:
        try:
            # The str() in this line is because OWM will accept
            # a zipcode but Salt and the YAML parser will convert it 
            # to an integer.  OWM wants a string.
            weather_result = __proxy__['owm.api']().weather_at_place(str(place))
            weather_json = weather_result.to_JSON()
        except pyowm.exceptions.not_found_error.NotFoundError:
            return 'Place not found.'

    weather_dictionary = json.loads(weather_json)

    return weather_dictionary


def list_stations():
    '''
    List details for all personal weather stations attached to 
    this API key.
    '''
    ret = {}
    stations = __proxy__['owm.sta']().get_stations()
    for station in stations:
        ret[station.id] = json.loads(station.to_JSON())

    return ret


def find_station(extid_or_id):
    '''
    Find a personal weather station by external_id or id.  Returns 
    station details or nothing if no match found.
    '''
    stations = __proxy__['owm.sta']().get_stations()

    station = [sta for sta in stations if sta.external_id == extid_or_id or sta.id == extid_or_id]

    if len(station) == 0:
        return {}

    return json.loads(station[0].to_JSON())


def add_station(external_id, name, latitude, longitude, elevation):
    '''
    Add a new personal weather station.
    external_id: Short identifier for the station
    name: Longer name or description for the station
    latitude and longitude: Valid latitude and longitude numbers (should be
        parseable as floating point numbers).  Note that
        the salt CLI might have trouble with negative numbers
        and interpret the dash as a CLI switch.  If this happens
        enclose the value in double and single quotes: "'-111.654'"
    Returns details for the new station.
    '''
    latitude = float(latitude)
    longitude = float(longitude)
    elevation = float(elevation)
    new_station = __proxy__['owm.sta']().create_station(external_id, name, latitude, longitude, elevation)
    return json.loads(new_station.to_JSON())


def delete_station(extid_or_id):
    '''
    Delete a pre-existing PWS.  Accepts an external_id or an id.
    If no station matches, return 'No match'.
    If more than one station matches, returns appropriate message
    and deletes none. If one station matches, deletes that 
    station and returns True.
    '''

    stations = __proxy__['owm.sta']().get_stations()

    station = [sta for sta in stations if sta.external_id == extid_or_id or sta.id == extid_or_id]

    if len(station) == 0:
        return 'No match'

    if len(station) > 1:
        return '{} matches more than one station.'.format(extid_or_id)

    result = __proxy__['owm.sta']().delete_station(station[0])

    return True
