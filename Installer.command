#!/usr/bin/env bash

PAUSE () {
	read  -n 8 -p "Type "continue" to move on: " throwAway; echo ""
}

GET_PYTHON3_MINOR_VERSION () {
pv=$(python3 --version)
if [ -z "$pv" ]; then
return $pv
fi

OLDIFS=$IFS
IFS="$." tokens=( $pv )
MINOR=${tokens[1]}
IFS=$OLDIFS
return $MINOR
}

## ----- Prompt user to install python 3.8.3 on their machine, so that the virtual environment can be created
# Do this first, because if the user doesn't want to install python, now you don't have other things to clean up!

# cd to the current file's location
bash_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$bash_path"

GET_PYTHON3_MINOR_VERSION; PYTHON3_MINOR_VERSION=$?
pv=$(python3 --version) # only checks for python3
if [ -z "$pv" ]; then # Check if the string is empty, which means there's no python 3
	curl -O "https://www.python.org/ftp/python/3.8.3/python-3.8.3-macosx10.9.pkg"
	open ./python-3.8.3-macosx10.9.pkg
	echo ""
	echo "You don't have Python3 installed at all"
	echo "Please install Python3"
	PAUSE
elif [ "$pv" = "$desired_python_version" ]; then # if the python the user has is Python3.8.3
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
	PAUSE
	curl -O "https://www.python.org/ftp/python/3.8.3/python-3.8.3-macosx10.9.pkg"
	open ./python-3.8.3-macosx10.9.pkg
	PAUSE
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
	echo ""
	echo ""
	echo "Hmm, it seems you chose to not download Python3."
	echo "And I know for a fact that this program cannot run on Python2."
	echo "You either didn't want to download Python, or you don't want to download Python3."
	echo "Which, hey, that's cool! :)"
	echo "Sooooo....."
	echo "The installation will stop. Thank you for being interested!"
	exit 0
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

## ----- If you made any changes to the file structure, fix it here
# Such as changing where venv is, then crontab needs to be updated