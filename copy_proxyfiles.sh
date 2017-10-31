#!/bin/bash
cd SaltStack_Network_Edge_Device
cp beacon/* $VE/salt/salt/beacons
cp modules/* $VE/salt/salt/modules
cp proxy/* $VE/salt/salt/proxy
cd $VE
