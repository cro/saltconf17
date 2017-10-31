# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import os.path
# Import python libs
import salt.utils.path
import logging

# Variables are scoped to this module so we can have persistent data
# across calls to fns in here.
GRAINS_CACHE = {}
DETAILS = {}

# Want logging!
log = logging.getLogger(__file__)

__proxyenabled__ = ['nodemcu']

def __virtual__():
    '''
    Check for esptool and nodemcu-uploader
    '''
    ESPTOOL = salt.utils.path.which('esptool')
    if not ESPTOOL:
        return (False, 'The NodeMCU proxymodule needs access to the esptool utility')
    UPLOADER = salt.utils.path.which('nodemcu-uploader')
    if not UPLOADER:
        return (False, 'The NodeMCU proxymodule needs access to the nodemcu-uploader utility')
    DETAILS['esptool'] = ESPTOOL
    DETAILS['uploader'] = UPLOADER
    return True


def init(opts):
    log.debug('nodemcu init() called...')
    DETAILS['initialized'] = False
    try:
        DETAILS['port'] = opts['proxy']['port']
    except KeyError:
        DETAILS['port'] = '/dev/ttyUSB0'
    try:
        DETAILS['baud'] = opts['proxy']['baud']
    except KeyError:
        DETAILS['baud'] = '115200'

    DETAILS['initialized'] = ping()

    return DETAILS['initialized']


def initialized():
    '''
    Since grains are loaded in many different places and some of those
    places occur before the proxy can be initialized, return whether
    our init() function has been called
    '''
    return DETAILS.get('initialized', False)


def ping():

    cmd = [DETAILS['esptool'], '--port', DETAILS['port'], '--baud', DETAILS['baud'], 'chip_id']

    tries = 0
    while tries < 3:
        tries = tries + 1
        result = __salt__['cmd.run_all'](cmd)
        if result['retcode'] != 0:
            log.debug('Tried getting the chip_id and got {}'.format(result['stdout']))
            continue
        else:
            break

    return result['retcode'] == 0


def list_files():

    cmd = ['nodemcu-uploader', '--port', DETAILS['port'], '--baud', DETAILS['baud'],
            'file', 'list']
    tries = 0
    while tries < 3:
        tries = tries + 1
        upload_result = __salt__['cmd.run_all'](cmd)
        log.debug(upload_result)
        if upload_result['retcode'] == 0:
            break
        log.info('Nodemcu file list timed out.  Try number {}'.format(tries))
        return upload_result

    found_files = False
    filenames = {}
    for line in upload_result['stderr'].splitlines():
        if line.startswith('for key,value'):
            found_files = True
            continue
        if line.startswith('>'):
            continue
        if found_files:
            log.debug(line)
            filename, size = line.split('\t')
            filenames[filename] = {'name': filename, 'size': size}

    return filenames


def reset_nodemcu():

    cmd = ['esptool', '--port', DETAILS['port'], '--baud', DETAILS['baud'],
            '--after', 'hard_reset', 'chip_id']
    tries = 0
    while tries < 3:
        tries = tries + 1
        reset_result = __salt__['cmd.run_all'](cmd)
        log.debug(reset_result)
        if reset_result['retcode'] == 0:
            break
        log.info('Nodemcu reset timed out.  Try number {}'.format(tries))
    return reset_result


def upload_file(source):

    ret = __salt__['cp.cache_file'](source)

    if ret:
        path = os.path.dirname(ret)
        filename = os.path.basename(ret)
        cmd = ['nodemcu-uploader', '--port', DETAILS['port'], '--baud', DETAILS['baud'],
                'upload', filename]
        tries = 0
        while tries < 3:
            tries = tries + 1
            upload_result = __salt__['cmd.run_all'](cmd, cwd=path)
            log.debug(upload_result)
            if upload_result['retcode'] == 0:
                break
            log.info('Nodemcu file upload timed out.  Try number {}'.format(tries))

        if upload_result['retcode'] == 0:
            return filename
        else:
            return upload_result
    else:
        return '{} not found'.format(source)


def delete_file(filename):

    cmd = ['nodemcu-uploader', '--port', DETAILS['port'], '--baud', DETAILS['baud'],
                'file', 'remove', filename]
    tries = 0
    while tries < 3:
        tries = tries + 1
        delete_result = __salt__['cmd.run_all'](cmd)
        if delete_result['retcode'] == 0:
            break
        log.info('Nodemcu file delete timed out.  Try number {}'.format(tries))

    if delete_result['retcode'] == 0:
        return True
    else:
        return delete_result


def run_file(name):

    cmd = ['nodemcu-uploader', '--port', DETAILS['port'], '--baud', DETAILS['baud'],
            'file', 'do', name]
    run_result = __salt__['cmd.run_all'](cmd)
    return run_result


def shutdown(opts):
    '''
    For this proxy shutdown is a no-op
    '''
    log.debug('NodeMCU proxy shutdown() called...')


