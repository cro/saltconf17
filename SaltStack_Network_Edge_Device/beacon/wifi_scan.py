import logging

log = logging.getLogger(__file__)
BEACON_DATA = {}

def beacon(config):
    '''
    Send an event when Wi-Fi access points appear.
    '''

    # Get our list of Access Points from our NodeMCU proxy minion
    found_aps = __salt__['nodemcu.scan']()

    # The first run through we don't have anything to compare with
    if 'aps' not in BEACON_DATA:
        BEACON_DATA['aps'] = found_aps
        return []

    # Compare the old and new BSSIDs
    old_keys = set(BEACON_DATA['aps'].iterkeys())
    new_keys = set(found_aps.iterkeys())

    # Remove all the APs we have seen before
    new_aps = new_keys - old_keys

    # If there are none left, return an empty list, this
    # tells the beacon subsystem that no event needs to be emitted
    if not new_aps:
        BEACON_DATA['aps'] = found_aps
        return []

    # There are some new APs, get their details and put them into
    # a dictionary for inclusion into the event.
    changes = {}
    for k in new_aps:
        changes[k] = found_aps[k]

    BEACON_DATA['aps'] = found_aps

    # Return the changes dictionary.  This causes the beacon subsystem to
    # emit the right events.
    return [{'changes': [changes], 'tag': 'new_aps'}]


