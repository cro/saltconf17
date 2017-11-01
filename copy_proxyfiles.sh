#!/bin/bash
cd SaltStack_Network_Edge_Device
echo "Copying beacons..."
cp beacon/* $VE/salt/salt/beacons
echo "Copying execution modules..."
cp modules/* $VE/salt/salt/modules
echo "Copying proxymodules..."
cp proxy/* $VE/salt/salt/proxy
echo "Copying Lua scripts..."
cp *.lua /srv/salt/files
echo "Done!"
cd $VE
