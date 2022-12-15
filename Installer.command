#!/usr/bin/env bash

# cd to the current file's location
bash_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$bash_path"

# Create the folders housing everything, if they don't exist
mkdir -p ~/AO3_Stats
mkdir -p ~/AO3_Stats/Data

# If the program already exists, delete it so that the new one can be installed
rm -r ~/AO3_Stats/Program

# Move the files
mv ./Program ~/AO3_Stats
mv ./AO3\ Stat\ Tracker.command ~/Desktop

# Give files permission
chmod +x ~/Desktop/AO3\ Stat\ Tracker.command
chmod +x ~/AO3_Stats/Program/common.py
chmod +x ~/AO3_Stats/Program/generate_graph.py
chmod +x ~/AO3_Stats/Program/interact_with_cron.py
chmod +x ~/AO3_Stats/Program/update_AO3_fics.py
chmod +x ~/AO3_Stats/Program/user_interface.py

# Install dependancies that were left out of the data transfer
cd ~/AO3_Stats/Program
source bin/activate
pip install -r requirements.txt
deactivate