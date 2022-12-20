#!/usr/bin/env python3
# This file contains a list of constants used throughout the project
# Author: Fixationally_Consumed
import os
import pathlib

""" File Directory
-- Cron
  |__ user crontab
-- Home
  |__ AO3 Stats
     |__ Program
     |  |__ common.py
     |  |__ generate_graph.py
     |  |__ interact_with_cron.py
     |  |__ update_AO3_fics.py
     |  |__ user_interface.py
     |  |__ <other environment folders>
     |
     |__ Data
        |__ AO3_fic_list_save_file.txt
        |__ <pickle files>
"""

""" Script interactions
                user_interface.py
                 A             \
                /               \
               V                 \
    interact_with_cron.py         |
               |                  |
               V                  V
            crontab        fic_save_list.txt
    <built into computer>       /
                       \       /
                        \     /
                          \ /
                           V
                    update_AO3_fics.py
                           |
                           V
                    generate_graph.py

"""

## Constants -------------------
SEP = ';;'

MAIN_DIR_NAME = 'AO3_Stats'
PROGRAM_DIR_NAME = 'Program'
DATA_DIR_NAME = 'Data'

HOME_DIR = str(pathlib.Path.home())
MAIN_DIRECTORY = os.path.join(HOME_DIR, MAIN_DIR_NAME)
PROGRAM_DIRECTORY = os.path.join(MAIN_DIRECTORY, PROGRAM_DIR_NAME)
DATA_DIRECTORY = os.path.join(MAIN_DIRECTORY, DATA_DIR_NAME)

#HISTORY_FOLDER_NAME = MAIN_DIR_NAME
#HISTORY_FOLDER_DIRECTORY = os.path.join(HOME_DIR, HISTORY_FOLDER_NAME)
HISTORY_FOLDER_DIRECTORY = DATA_DIRECTORY

#FIC_SAVE_FOLDER_NAME = MAIN_DIR_NAME
FIC_SAVE_DICRECTORY = DATA_DIRECTORY
FIC_SAVE_FILENAME = 'AO3_fic_list_save_file.txt'
FIC_SAVE_FILEPATH = os.path.join(FIC_SAVE_DICRECTORY, FIC_SAVE_FILENAME)

## Functions -------------------
def make_graph_filename(ficName):
    return f"{ficName} - stats.png"

def make_workHistory_filename(ficName, ID):
    return f"{ficName}_{ID}_workHistory.pickle"

def ensure_fic_save_file_exists(fic_save_filepath):
    fic_save_directory = os.path.dirname(fic_save_filepath)
    # Create the save folder if it doesn't already exist
    if not os.path.exists(fic_save_directory):
        os.makedirs(fic_save_directory)
    # Create the save file if it doesn't already exist
    if not os.path.exists(fic_save_filepath):
        with open(fic_save_filepath, 'w') as fh:
            fh.write('')
    return None

def read_in(filepath):
    fic_obj = list()
    with open(filepath, 'r') as fh:
        split_raw_text = fh.readlines()

    processed_split_raw_text = list()
    for line in split_raw_text:
        line = line.strip()
        if line == '': # Either blank spaces or new lines
            continue
        processed_split_raw_text.append(line)
    
    for line in processed_split_raw_text:
        workID, ficName, graphDirectory = line.split(SEP)
        fic_obj.append({'workID':workID,
                    'ficName': ficName,
                    'graphDirectory': graphDirectory})
    return fic_obj

def write_out(fics_obj, filepath, alterFicNumber=None):
    if len(fics_obj) > 0:
        with open(filepath, 'w') as fh:
            for fic in fics_obj:
                line = SEP.join([fic['workID'], fic['ficName'], fic['graphDirectory']]) + '\n'
                fh.write(line)
    else:
        with open(filepath, 'w') as fh:
            fh.write('')
    return None

def clear_screen(new_lines=20):
    print('\n'*new_lines)
    return None

def isPosInt(string):
    for char in string:
        if char not in '0123456789':
            return False
    return True
