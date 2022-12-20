#!/usr/bin/env python3
# interact_with_fic_save_file.py: This allows the user to interact with the data file
#   that is referenced to update fics.
# Author: Fixationally_Consumed
import os
import shutil
from copy import copy
import pathlib
import AO3
from tabulate import tabulate
import warnings
# User Defined modules
import common as cm
import update_AO3_fics
import interact_with_cron

def print_fics(fics):
    if len(fics) < 1:
        print("You have no fics you're currently tracking.")
        return None

    # Create a list of lists for the tabulate function
    data = list()
    for index, fic in enumerate(fics):
        data.append([str(index), fic['workID'], fic['ficName'], fic['graphDirectory']])

    print(tabulate(data, headers=['Index', 'Work ID', 'Fic Name', 'Graph Directory']))
    return None

def is_valid_AO3_workID(workID):
    # Returns True if work ID is identifiable on AO3
    workID = int(workID) # Make sure work ID is an int

    warnings.filterwarnings(action='ignore', category=UserWarning, module='AO3') # Suppress the annoying UserWarning that some fics may be long in length
    try:
        AO3.Work(workID)
        return True
    except AO3.utils.InvalidIdError:
        return False
    except Exception as e:
        if 'Failed to establish a new connection' in str(e):
            cm.clear_screen(new_lines=3)
            print("Hmmm... it seems you don't have internet connection, which is needed to validate this work ID.")
            print("The entered ID is assumed to be valid, but if it's wrong then the program won't update this fic.")
            print('Press any button to accept this and continue.')
            input()
            return True
        else:
            raise e
    
def get_workID(fics):
    # Returns the work ID of the fic the user wants to track. The function ensures the work ID is valid.
    print('Every fic on AO3 has a work ID, which is a number, associated with it.')
    print('For example, in the URL')
    print('https://archiveofourown.org/works/32751484/chapters/81257581')
    print('The work ID is 32751484.')
    while True:
        print('Please enter the work ID of the fic you want to track, or copy/paste the URL of the fic.\n')
        ID_or_URL = input().strip()
        
        # Sort out if they passed in a workID or the URL, then pull out the ID if necessary
        if len(ID_or_URL) > 26: # The only reason it would be this long is if it were a URL they'd pasted in
            URL = ID_or_URL
            try:
                possible_ID = str(AO3.utils.workid_from_url(URL))
            except:
                cm.clear_screen()
                print('Sorry, the script could not identify the work ID.')
                print('Try pasting the full URL again or manually entering it.')
                continue
            if not cm.isPosInt(possible_ID):
                cm.clear_screen()
                print(f'Sorry, the script identified\n{ID}\nfrom\n{URL}\nPlease try again or type in the work ID manually.')
                continue
            ID = possible_ID
        elif len(ID_or_URL) > 0 and cm.isPosInt(ID_or_URL):
            ID = ID_or_URL
        else:
            cm.clear_screen()
            print(f'The value\n"{ID_or_URL}"\nis not identifiable. Please enter it again.')
            continue

        cataloged_IDs = {cataloged_fic['workID'] for cataloged_fic in fics}
        if ID in cataloged_IDs:
            cm.clear_screen()
            print('Sorry, this ID is already being used by another fic you\'re tracking.')
            print('Please enter another work ID.')
            continue
        elif not is_valid_AO3_workID(ID):
            cm.clear_screen()
            print('Sorry, this ID is not identifiable on AO3.')
            print('Please make sure you typed in the correct ID and/or pasted the correct URL')
            print('If the program doesn\'t detect the correct work ID from the URL, try typing it manually.')
            continue
        else:
            cm.clear_screen()
            return ID
    return None

def includes_illegal_char(string):
    illegal_chars = '/<>:"\|?*;'
    windows_illegal_names = """CON, PRN, AUX, NUL, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9""".split(', ')
    for char in string:
        if char in illegal_chars:
            return True
    if string in windows_illegal_names:
        return True
    elif string.endswith(' ') or string.endswith('.'):
        return True
    else:
        return False
    return None
    
def get_ficName(fics):
    while True:
        print('What is the name of the fic?')
        print('Please omit any special characters other than _ and -')
        print('Note: You can shorten or abbreviate this for ease.')
        ficName = input().strip()
        if includes_illegal_char(ficName):
            cm.clear_screen()
            print(f'{ficName} is not allowed, sorry :/')
            print('Please do not use any special characters or end with a period.')
            print('There are also some abbreviations that aren\'t allowed. Sorry.')
            print('Please enter another fic name.')
            print()
            continue
        cataloged_names = {cataloged_fic['ficName'] for cataloged_fic in fics}
        if ficName in cataloged_names:
            cm.clear_screen()
            print(f'{ficName} is already used for another fic being tracked.')
            print('Please chose another name.')
            print()
            continue
        print()
        print(ficName)
        print('Did the name print above how you want it to be named?')
        if input('Type "Yes" or "No" to continue: ').lower().startswith('y'):
            cm.clear_screen()
            return ficName
        cm.clear_screen()
    return None

def get_graphDirectory():
    # Returns the directory of where the user wants the graph stored
    # Also adds on to the path a new folder where the save files will be kept
    print('Would you like the graph to be stored on your Desktop (recommended)?')
    print('Type "Yes" or "No" to continue, then enter: ')
    if input().lower().startswith('y'):
        directory = os.path.join(str(pathlib.Path.home()),'Desktop')
    else:
        print('Enter the absolute path to the directory/folder where you want the graph to be located.')
        print('After typing the path, hit Enter.')
        print('Hint: You can also drag and drop the folder in this window to paste the path.')
        print('You can also enter a blank line and the program will default to the Desktop')
        directory = input().replace('\\','') # Python does not need or use \ to denote spaces in directories
        while not os.path.exists(directory):
            """When dragged and dropped in, the terminal adds a space at the end (annoying).
            If the directory given doesn't exist (checked above)
            then check to see if the same directory exists but with the space removed.
            If so, use that directory instead. This removes the error of the possibility that
            the user, for some reason, does have a directory with a space at the end."""
            if len(directory) > 0 and directory[-1] == ' ' and os.path.exists(directory[:-1]):
                directory = directory[:-1]
                break
            
            cm.clear_screen()
            print('That directory/folder does not exist. Please enter it again or try a new folder.')
            print('\n')
            print('Enter the absolute path to the directory/folder where you want the graph to be located.')
            print('After typing the location, hit Enter.')
            print('Hint: You can also drag and drop the folder in this window to paste the path.')
            print()
            print('You can also enter a blank line and the program will default to the Desktop')
            directory = input().replace('\\','') # Python does not need or use \ to denote spaces in directories
            if directory == '':
                directory = os.path.join(str(pathlib.Path.home()), 'Desktop')
                break
    cm.clear_screen()
    return directory

def change_fic_save_files(old_fic, new_fic):
    # Changes the save locations and/or names of the save files
    #   If nothing has been changed, the function won't change anything.
    #   If the work ID is the only thing that changed, nothing gets updated.
    # Move/Rename graph
    old_graph_filepath = os.path.join(old_fic['graphDirectory'], cm.make_graph_filename(old_fic['ficName']))
    new_graph_filepath = os.path.join(new_fic['graphDirectory'], cm.make_graph_filename(new_fic['ficName']))
    if os.path.exists(old_graph_filepath):
        shutil.move(old_graph_filepath, new_graph_filepath)
##    else:
##        # The file hasn't actually been made yet and this is a fic list clerical change
##        # Nothing else needs to be done

    # Update the name of the work history pickle file if the name changed
    old_workHistory_filepath = os.path.join(cm.DATA_DIRECTORY, cm.make_workHistory_filename(old_fic['ficName'], old_fic['workID']))
    new_workHistory_filepath = os.path.join(cm.DATA_DIRECTORY, cm.make_workHistory_filename(new_fic['ficName'], new_fic['workID']))
    if os.path.exists(old_workHistory_filepath):
        os.rename(old_workHistory_filepath, new_workHistory_filepath)
    return None

def change_fic_list(fics, save_filepath):
    if len(fics) < 1:
        print('There are no fics to change.')
        return fics
    
    while True:
        print_fics(fics)
        print()
        print('Warning: Any accepted changes made are saved immediately.')
        print('If you make a change you don\'t want, just change it again!')
        print()
        print('Please type a command. After typing, hit Enter.')
        print('Change a row:                           Type the row number')
        print('Save and return to home screen:         Type "Save"')
        command = input()
        if command.lower().startswith('s'):
            cm.write_out(fics, save_filepath)
            return fics
        elif cm.isPosInt(command) and int(command) < len(fics):
            fic = fics.pop(int(command))
            unchanged_fic = copy(fic)
            cm.clear_screen()
            print(f'You have chosen to change {command}')
            print('Work ID: --------------- ' + fic['workID'])
            print('Fic Name: -------------- ' + fic['ficName'])
            print('Directory of Graph File: ' + fic['graphDirectory'])
            
            # Pull new fic data from user
            print()
            print('If you mis-type or wish to exit, simply type in fake values or accept the defaults.')
            print('The program will then ask if you wish to accept this change, and you can decline then.')
            print()
            workID = get_workID(fics)
            ficName = get_ficName(fics)
            graphDirectory = get_graphDirectory()
            print('\n')
            print(f'Do you accept row {command} new values?')
            print('Work ID: --------------- ' + workID)
            print('Fic Name: -------------- ' + ficName)
            print('Directory of Graph File: ' + graphDirectory)
            print('Type "Yes" to accept and "No" to decline')
            if input().lower().startswith('y'):
                fic = {'workID': workID,
                       'ficName': ficName,
                       'graphDirectory': graphDirectory}
                change_fic_save_files(unchanged_fic, fic)
                fics.insert(int(command), fic)
                cm.write_out(fics, save_filepath)
                cm.clear_screen()
            else:
                cm.clear_screen()
                print(f'Okay, Index {command} will not be changed.')
                print('If that was a mistake, please enter the information again.')
                fics.insert(int(command), unchanged_fic)
        else:
            cm.clear_screen()
            print(f'\nThe command "{command}" is not recognized or not listed.')
            print('Please try typing it again.')
            print()
    return None

def add_to_fic_list(fics, save_filepath):
    unchanged_fics = copy(fics)
    while True:
        print_fics(fics)
        print()
        print('Please type a command. After typing, hit Enter.')
        print('Add a fic:                              Type "Add"')
        print('Save:                                   Type "Save"')
        print('Quit without saving additions:          Type "Quit"')
        command = input()
        if command.lower().startswith('s'):
            cm.write_out(fics, save_filepath)
            return fics
        elif command.lower().startswith('q'):
            return unchanged_fics
        elif command.lower().startswith('a'):
            # Pull new fic data from user
            cm.clear_screen()
            print('If you mis-type or wish to exit, simply type in fake values or accept the defaults.')
            print('The program will then ask if you wish to accept this addition, and you can decline then.')
            print()
            workID = get_workID(fics)
            ficName = get_ficName(fics)
            graphDirectory = get_graphDirectory()
            print('\n\n')
            print('Do you wish to add the following fic?')
            print('Work ID: --------------- ' + workID)
            print('Fic Name: -------------- ' + ficName)
            print('Directory of Graph File: ' + graphDirectory)
            print('Type "Yes" to accept and "No" to decline')
            if input().lower().startswith('y'):
                fics.append({'workID': workID,
                             'ficName': ficName,
                             'graphDirectory': graphDirectory})
                cm.clear_screen()
            else:
                cm.clear_screen()
                print('Okay, this will not be added.')
                print('If that was a mistake, please enter the information again.')
        else:
            cm.clear_screen()
            print(f'\nThe command {command} is not recognized.')
            print('Please enter another command.')
            print()
    return None

def delete_from_fic_list(fics, save_filepath):
    if len(fics) < 1:
        print('There are no fics to delete.')
        return fics
    unchanged_fics = copy(fics)
    
    while True:
        print_fics(fics)
        print()
        print('Deleting a fic will only stop it from being tracked. It\'s data will still be stored.')
        print()
        print('Please enter a command. After typing, hit Enter.')
        print('Delete a row:                           Type the Index number')
        print('Save:                                   Type "Save"')
        print('Quit without saving deletions:          Type "Quit"')
        row = input()
        if row.lower().startswith('s'): # Save the fic list
            cm.write_out(fics, save_filepath)
            return fics
        elif row.lower().startswith('q'): # Quit without saving
            return unchanged_fics
        elif cm.isPosInt(row) and len(fics) < 1:
            cm.clear_screen()
            print('\nThere are no more fics to delete. Please save or quit without saving these changes.')
        elif cm.isPosInt(row) and int(row) < len(fics):
            cm.clear_screen()
            print(f"{row}  |  {fics[int(row)]['ficName']}")
            print()
            # Ask and make sure they want to delete this row
            if input(f'\nAre you sure you want to stop updating Row {row}?\nType "Yes" or "No": ').lower().startswith('y'):
                # At this point, the user is sure they want to delete this row
                del fics[int(row)]
            cm.clear_screen()
        else:
            cm.clear_screen()
            print(f'\nThe command "{row}" is not recognized or not listed.')
            print('Please try typing it again.')
            print()
    return None

def user_interface(save_filepath):
    # Loop that allows the user to interact with and change the file commanding what fics are tracked.
    #   This will also move and/or rename the stat files if the user changes those in any way.
    cm.ensure_fic_save_file_exists(save_filepath) # Also creates the save folder if it doesn't exist
    cm.clear_screen()
    
    print('Hi!\n')
    while True:
        fics = cm.read_in(save_filepath)
        print('What would you like to do? After typing, hit Enter')
        print('View fics being tracked:             Type "View"')
        print('Add a fic to be tracked:             Type "Add"')
        print('Remove a fic from tracking:          Type "Remove"')
        print('Change a fic in tracking:            Type "Change"')
        print('Adjust time fics are tracked:        Type "Time"')
        print('                   ~~~~~~~~~~             ')
        print('Update the fics right now:           Type "Update"')
        print('Exit program:                        Type "Exit"')
        print('                   ~~~~~~~~~~             ')
        
        user_action = input()
        if user_action.lower().startswith('v'): # View fics
            cm.clear_screen()
            print_fics(fics)
            print()
        elif user_action.lower().startswith('a'): # Add a fic
            cm.clear_screen()
            fics = add_to_fic_list(fics, save_filepath)
            cm.clear_screen()
        elif user_action.lower().startswith('r'): # Remove a fic
            cm.clear_screen()
            fics = delete_from_fic_list(fics, save_filepath)
            cm.clear_screen()
        elif user_action.lower().startswith('c'): # Change a fic
            cm.clear_screen()
            fics = change_fic_list(fics, save_filepath)
            cm.clear_screen()
        elif user_action.lower().startswith('e'): # Save the changes and exit
            cm.write_out(fics, save_filepath)
            return None
        elif user_action.lower().startswith('u'): # Save and update the fics right now
            cm.write_out(fics, save_filepath)
            cm.clear_screen()
            print('Updating fics...')
            update_AO3_fics.update_AO3_fics(cm.FIC_SAVE_FILEPATH)
            cm.clear_screen()
        elif user_action.lower().startswith('t'): # Change the times the script is tracked
            cm.clear_screen()
            interact_with_cron.interact_with_cron()
            cm.clear_screen()
        else:
            cm.clear_screen()
            print(f"Command not identified - '{user_action}'")
            print('Please re-enter your command')
    return None

if __name__ == '__main__':
    user_interface(cm.FIC_SAVE_FILEPATH)
