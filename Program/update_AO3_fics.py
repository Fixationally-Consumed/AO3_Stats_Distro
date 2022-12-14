#!/usr/bin/env python3
# main.py:  Runs the script that takes in data and commands the computer to update the fics being tracked.
# Author: Fixationally_Consumed
from generate_graph import generate_graph
import os
import pathlib
import common as cm
import datetime

def update_AO3_fics(fic_save_filepath):
    cm.ensure_fic_save_file_exists(fic_save_filepath)
    list_of_fics = cm.read_in(fic_save_filepath)
    for fic in list_of_fics:
        try:
            # If cm.HISTORY_FOLDER_DIRECTORY does not exist, generate_graph will create a new file
            print('Updating: ', fic['ficName'], '...')
            generate_graph(int(fic['workID']), fic['ficName'], fic['graphDirectory'], cm.HISTORY_FOLDER_DIRECTORY)

        except Exception as e:
            if 'Failed to establish a new connection' in str(e):
                print('There was no internet connection on ', datetime.date.today())
                print('The fics were not updated.')
                break # No need to continue with all of them if there's no connection
            else:
                # If there's an issue with the program, just skip this fic
                print(f"Error with {fic['ficName']} on {datetime.date.today()}")
                raise e
                print(e)
                continue
    return None

if __name__  == '__main__':
    update_AO3_fics(cm.FIC_SAVE_FILEPATH)
