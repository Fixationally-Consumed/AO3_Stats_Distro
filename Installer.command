#!/usr/bin/env bash

## ----- Functions and constants

PAUSE () {
	read  -n 8 -p "Type "continue" to move on: " throwAway; echo ""
}

GET_PYTHON3_MINOR_VERSION () {
pv=$(python3 --version)
if [[ ${pv} != *"Python"* ]]; then # if pv doesn't contain "Python", meaning that the script returned an error code or an empty
	WAS_PYTHON3_INSTALLED=$"False"
	return $0
	# I cannot figure out how to return a value within MINOR unless it's a number. So instead, I'm assigning the flag to a global variable
else
	WAS_PYTHON3_INSTALLED=$"True"
fi

OLDIFS=$IFS
IFS="$." tokens=( $pv )
MINOR=${tokens[1]}
IFS=$OLDIFS
return $MINOR
}

PYTHON_DOWNLOAD=$"https://www.python.org/ftp/python/3.8.3/python-3.8.3-macosx10.9.pkg"
PYTHON_INSTALLER=$"./python-3.8.3-macosx10.9.pkg"

## ----- Explain to the user how this is going to work
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo "Hello"
echo "I see you would like to download my AO3 stats program."
echo "Isn't that wonderful :D"
echo "Below is some instructions about how this installer will work."
echo ""
echo "1) You may be prompted to download python. If so, this installer will open"
echo "the correct python installer for you :)"
echo ""
echo "2) At times, the installer may ask you to type the word continue."
echo "Please do as it says. FYI, you won't be able to delete spaces (because"
echo "it's only really looking for 8 letters to be entered. It was the best"
echo "that I could do.)"
echo ""
echo "3) Some of the installation may 'freeze' up, but I promise it hasn't."
echo "Give it some time. It may take 2-3 minutes to download everything."
echo ""
echo "4) You'll know when the program has completed it's downloading when the"
echo "screen says [Process completed]. Only then should you close the installer."
echo ""
echo "5) I'm sure you saw the 'Unidentified Developer' thing trying to run this."
echo "It was annoying, I'm sure. It'll appear once more the first time you try"
echo "to run my program. Follow the steps again in the picture provided, and then"
echo "you'll never have to deal with it again (unless you download this a second time)."
echo ""
echo "6) Once everything is completed, you'll find a file named"
echo "'AO3 Stat Tracker.command' on your desktop. You may move it where you like,"
echo "and this is the file you'll double click on to run the installed program."
echo ""
echo "Now, continue on to install :D"
echo ""
PAUSE

## ----- Prompt user to install python 3.8.3 on their machine, so that the virtual environment can be created
# Do this first, because if the user doesn't want to install python, now you don't have other things to clean up!

# cd to the current file's location
bash_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$bash_path"

GET_PYTHON3_MINOR_VERSION; PYTHON3_MINOR_VERSION=$?
if [ $WAS_PYTHON3_INSTALLED = $"False" ]; then # Check if the flag is False, which means there's no python 3
	curl -O $PYTHON_DOWNLOAD
	open $PYTHON_INSTALLER
	echo ""
	echo "You don't have Python3 installed at all"
	echo "Please install Python3"
	PAUSE
elif [ "$PYTHON3_MINOR_VERSION" = "8" ]; then # if the python the user has is Python3.8
	echo "Python 3.8 is already installed. Continuing on...";
else # The user has python3, but it's not my version
	echo "You have python3, but not the version the code was written with."
	echo "The installer is about to ask you to install python3.8.3."
	echo "I know that this is at least compatible with with python3.8.3."
	echo "If you have a later version, that'll probably work too."
	echo "You may want to decline the python installation that is about to happen,"
	echo "so you don't install multiple versions of python."
	echo ""
	echo "If you decline the upcoming download request (by simply closing out of it),"
	echo "this installer will still try to continue on with your current version of python."
	echo " "
	PAUSE
	curl -O $PYTHON_DOWNLOAD
	open $PYTHON_INSTALLER
	PAUSE
fi

# Check to make sure python was installed.
# The possible options are
#	1) The user didn't have python and didn't want to install it
#	2) The user didn't have python and installed Python 3.8.3
#	3) The user didn't have python and instead installed another version
#	4) The user already had Python 3.8.3
#	5) The user already had another version of Python3 and didn't download Python3.8.3
#	6) The user had a version of Python2 and wanted to stick with it
# How to deal with these
#	1) Cancel the install
#	2) Continue
#	3) Try to continue
#	4) Continue
#	5) Try to continue
#	6) Cancel the install
# Checking again for if the user has python3 will handle all of the "Cancel the install" scenarios above

GET_PYTHON3_MINOR_VERSION; PYTHON3_MINOR_VERSION=$?
if [ $WAS_PYTHON3_INSTALLED = $"False" ]; then
	echo ""
	echo ""
	echo "Hmm, it seems you chose to not download any version of Python3."
	echo "And I know for a fact that this program cannot run on Python2."
	echo "You either didn't want to download Python, or you don't want to download Python3."
	echo "Which, hey, that's cool! :)"
	echo "Sooooo....."
	echo "The installation will stop. Thank you for being interested!"
	exit 0
fi

echo "This is the end of the Python installation"

## ----- Moving files from download
# cd to the current file's location
bash_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$bash_path"

# Create the folders housing everything, if they don't exist
mkdir -p ~/AO3_Stats
mkdir -p ~/AO3_Stats/Data

# If the program already exists, delete it so that the new one can be installed
rm -r ~/AO3_Stats/Program
rm ~/Desktop/AO3\ Stat\ Tracker.command

# Move the files
cp -r ./Program ~/AO3_Stats
cp -r ./AO3\ Stat\ Tracker.command ~/Desktop

# Give files permission
chmod +x ~/Desktop/AO3\ Stat\ Tracker.command
chmod +x ~/AO3_Stats/Program/common.py
chmod +x ~/AO3_Stats/Program/generate_graph.py
chmod +x ~/AO3_Stats/Program/interact_with_cron.py
chmod +x ~/AO3_Stats/Program/update_AO3_fics.py
chmod +x ~/AO3_Stats/Program/user_interface.py

echo "This is the end of the file movements"

## ----- Installing dependancies with python
cd ~/AO3_Stats/Program

# Install virtualenv if not installed
python3 -m pip install virtualenv # Installs under the user (not the root) I'm pretty sure
# To uninstall virtualenv (under the user) use # pip3 uninstall virtualenv

# Create the virtual environment inside of the Project
python3 -m virtualenv venv

# Install dependancies that were left out of the data transfer
source venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate

echo "This is the end of the package installations"

## ----- If you made any changes to the file structure, fix it here
# Such as changing where venv is, then crontab needs to be updated