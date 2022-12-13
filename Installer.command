#!/usr/bin/env bash

bash_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$bash_path"

mv ./AO3_Stats ~
mv ./AO3\ Stat\ Tracker.command ~/Desktop


chmod +x ~/Desktop/AO3\ Stat\ Tracker.command
chmod +x ~/AO3_Stats/Program/user_interface.py