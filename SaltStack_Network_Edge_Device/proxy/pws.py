# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Import python libs
import logging
import pyowm

# Variables are scoped to this module so we can have persistent data
# across calls to fns in here.
GRAINS_CACHE = {}
DETAILS = {}

# Want logging!
log = logging.getLogger(__file__)

__proxyenabled__ = ['pws']
try:
    import pyowm
    HAS_PYOWM = True
except ImportError as exc:
    HAS_PYOWM = FALSE

def __virtual__():
    '''
    Only return if all the modules are available
    '''
    if HAS_PYOWM:
        return True
    else:
        return (HAS_PYOWM, 'Cannot import pyowm.')


def init(opts):
    log.debug('pws init() called...')
    DETAILS['initialized'] = False
    try:
        DETAILS['apikey'] = opts['proxy']['apikey']
        DETAILS['pwsid'] = opts['proxy']['pwsid']
        DETAILS['owm_object'] = pyowm.OWM(DETAILS['apikey'])
        DETAILS['stations_manager'] = DETAILS['owm_object'].stations_manager()
        DETAILS['station'] = DETAILS['stations_manager'].get_station(DETAILS['pwsid'])
        DETAILS['initialized'] = True
    except KeyError:
        log.warning('OpenWeatherMap proxy needs an OpenWeatherMap API key in the proxy configuration.')

    return DETAILS['initialized']


def initialized():
    return DETAILS.get('initialized', False)


def alive(opts):
    return True


def ping():
    '''
    Does this station still exist?
    '''
    try:
        base_api_online = DETAILS['owm_object'].is_API_online()
    except UnauthorizedError as exc:
        log.warning('OpenWeatherMap proxy says the configured API key is not valid')
        log.warning(str(exc))
        return False

    try:
        DETAILS['station'] = DETAILS['stations_manager'].get_station(__opts__['proxy']['pwsid'])
        return True
    except Exception as exc:
        log.warning(str(exc))
    return False


def shutdown(opts):
    '''
    For this proxy shutdown is a no-op
    '''
    log.debug('OpenWeatherMap proxy shutdown() called...')

def pwsid():
    return DETAILS['pwsid']

def api():
    return DETAILS['owm_object']

def sta():
    return DETAILS['stations_manager']

def station():
    return DETAILS['station']
