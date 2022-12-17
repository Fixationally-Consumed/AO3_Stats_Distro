#!/usr/bin/env bash

## ----- Prompt user to install python 3.8.3 on their machine, so that the virtual environment can be created
# Do this first, because if the user doesn't want to install python, now you don't have other things to clean up!

desired_python_verion=$"Python 3.8.3"
pv=$(python3 --version) # only checks for python3
if [ -z "$pv" ]; then # Check if the string is empty, which means there's no python 3
	echo "You dont have Python3 installed at all"
	echo "Please install Python3"
	open ./python-3.8.3-macosx10.9.pkg
elif [ "$pv" = "$desired_python_verion" ]; then # if the python the user has is Python3.8.3
	echo "Python 3.8.3 is already installed. Continuing on...";
else # The user has python3, but it's not my version
	echo "You have python3, but not the version the code was written with"
	echo "The installer is about to ask you to install python3.8.3"
	echo "I know that this is at least compatible with with python3.8.3."
	echo "If you have a later version, that'll probably work too."
	echo "You may want to decline the python installation that is about to happen,"
	echo "so you don't install multiple versions of python."
	echo "If you decline the upcoming download request, this installer will still continue on"
	echo "with your current version of python."
	echo " "
	echo "Press enter to continue"
	pause
	open ./python-3.8.3-macosx10.9.pkg
fi

# Check to make sure python was installed.
# The possible options are
#	1) The user didn't have python and didn't want to install it
#	2) The user didn't have python and installed Python 3.8.3
#	3) The user didn't have python and instead installed another version
#	4) The user already had Python 3.8.3
#	5) The user already had another version of Python3
#	6) The user had a version of Python2 and wanted to stick with it
# How to deal with these
#	1) Cancel the install
#	2) Continue
#	3) Try to continue
#	4) Continue
#	5) Try to continue
#	6) Cancel the install
# Checking again for if the user has python3 will handle all of the "Cancel the install" scenarios above

pv=$(python3 --version) # only checks for python3
if [ -z "$pv" ]; then
	echo "Hmm, it seems you chose to not download Python3."
	echo "Or maybe you think this'll work on your version of Python2."
	echo "Bold of you to assume my code is written that well."
	echo "If you're really wanting to take a stab at it,"
	echo "type Y (capitalized) and the installer will keep running."
	echo "Otherwise, the installer will discontinue."
	echo -n "Enter Y/n for Yes/no: "; read USER_INPUT
	if [ ! $USER_INPUT = "Y" ]; then
		exit 0
	fi
fi


## ----- Moving files from download
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

## ----- Installing dependancies with python
cd ~/AO3_Stats/Program

# Install virtualenv if not installed
pip install virtualenv

# Create the virtual environment inside of the Project
virtualenv venv

# Install dependancies that were left out of the data transfer
source venv/bin/activate
pip install -r requirements.txt
deactivate