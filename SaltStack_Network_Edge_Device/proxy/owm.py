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

__proxyenabled__ = ['owm']

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
    log.debug('owm init() called...')
    DETAILS['initialized'] = False
    try:
        DETAILS['apikey'] = opts['proxy']['apikey']
        DETAILS['owm_object'] = pyowm.OWM(DETAILS['apikey'])
        DETAILS['stations_manager'] = DETAILS['owm_object'].stations_manager()
        DETAILS['initialized'] = ping()
    except KeyError:
        log.warning('OpenWeatherMap proxy needs an OpenWeatherMap API key in the proxy configuration.')

    return DETAILS['initialized']


def initialized():
    '''
    Since grains are loaded in many different places and some of those
    places occur before the proxy can be initialized, return whether
    our init() function has been called
    '''
    return DETAILS.get('initialized', False)


def alive(opts):
    return True


def ping():
    '''
    Is OWM available?
    '''
    try:
        return DETAILS['owm_object'].is_API_online()
    except UnauthorizedError as exc:
        log.warning('OpenWeatherMap proxy says the configured API key is not valid')
        log.warning(str(exc))

    return False


def shutdown(opts):
    '''
    For this proxy shutdown is a no-op
    '''
    log.debug('OpenWeatherMap proxy shutdown() called...')

def sta():
    return DETAILS['stations_manager']

def api():
    return DETAILS['owm_object']
