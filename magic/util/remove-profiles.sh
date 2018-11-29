#!/bin/bash

# Removes all the installed network user profiles based upon a username and a ssid prefix.
# usage:
#   sudo ./remove-profiles <ssid prefix> <username from whoami>
# example:
#   sudo ./remove-profiles magic josephjung

SSID=$1
USER=$2

echo "Removing profiles for user:$USER and SSID: $SSID"

for line in $(profiles list -user=$USER | grep -Eo "profileIdentifier: $SSID-(.+)" | awk '{print $2} '); do
    echo "Removing profile via identifier: $line"
    profiles remove -identifier=$line -user=$USER
done

