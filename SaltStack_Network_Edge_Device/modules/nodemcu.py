# Execution module for interfacing with the nodemcu proxyminion.
import json

AUTH_TYPES = ('Open', 'WEP', 'WPA_PSK', 'WPA2_PSK', 'WPA_WPA2_PSK', 'WPA_Enterprise_Mixed')


def upload(name):
    return __proxy__['nodemcu.upload_file'](name)


def run(name):
    return __proxy__['nodemcu.run_file'](name)


def list():
    return __proxy__['nodemcu.list_files']()


def delete(name):
    return __proxy__['nodemcu.delete_file'](name)


def reset():
    return __proxy__['nodemcu.reset_nodemcu']()


def scan():
    scan_results = run('scan_results.lua')
    scan_dictionary = {}
    for line in scan_results['stderr'].splitlines():
        if line.startswith('=+-=+-=+-'):
            continue
        if line.startswith('None'):
            return {}
        if line.startswith('{'):
            scan_dictionary = json.loads(line)
        if line.startswith('>'):
            continue
        if line.startswith('--done--'):
            break

    scan_parsed = {}
    for k, v in scan_dictionary.iteritems():
        ap_details = v.split(',')
        auth_type = int(ap_details[2])
        try:
            auth_type_string = AUTH_TYPES[auth_type]
        except IndexError:
            auth_type_string = 'Unknown'
        scan_parsed[k] = { 'ssid': ap_details[0],
                           'rssi': ap_details[1],
                           'authtype': AUTH_TYPES[auth_type],
                           'channel': ap_details[3]
                           }
    return scan_parsed

