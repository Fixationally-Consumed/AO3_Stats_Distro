#!/usr/bin/env python
# Author: Fixationally_Consumed
from crontab import CronTab
from tabulate import tabulate
import common as cm
import re
from datetime import datetime
import os

# Constants --------
PYTHON_EXE_PATH = os.path.join(cm.PROGRAM_DIRECTORY, 'venv/bin/python3')
UPDATE_AO3_FICS_PATH = os.path.join(cm.PROGRAM_DIRECTORY, 'update_AO3_fics.py')
AO3_cron_command = ' '.join([PYTHON_EXE_PATH, UPDATE_AO3_FICS_PATH])

def get_AO3_jobs(cron):
    return [job for job in cron if job.command == AO3_cron_command]

def convert_weekdays(weekdays):
    conversion = {'0':'Sun', '1':'Mon', '2':'Tue', '3':'Wed', '4':'Thu', '5':'Fri', '6':'Sat', '*':'All'}
    individual_days = weekdays.split(',')
    conv_individual_days = [conversion[day] for day in individual_days]
    return ','.join(conv_individual_days)

def print_AO3_jobs(AO3_jobs):
    if len(AO3_jobs) < 1:
        print('There are no current times AO3 data is being collected.')
        return None
    data = list()
    for index, job in enumerate(AO3_jobs):
        minute = str(job.minute)
        hour = str(job.hour)
        weekdays = str(job.dow)
        data.append([index, hour, minute, convert_weekdays(weekdays)])
    print(tabulate(data, headers=['Index', '24-Hour', 'Minute', 'Day(s)']))
    return None

def get_time():
    # Returns an hour and time suitable for use with crontab
    # Prompts the user for the time of day (hour and minute) they wish for the program to run.
    # How it works
    #   1) Prompts the user for the time
    #   2) Use regex to pull out the hour, minute, and am/pm. Regex is much more versatile than the datetime function
    #   3) Clean up the numbers so they make sense (13:30pm doens't exist). Datetime is not versatile with this.
    #   4) Use datetime to convert to 24-hour if in am/pm

    while True:
        ##  ----- Prompt user for time
        print('Enter the time of day you want AO3\'s stats to be captured.')
        print('You can specify am, pm, or enter in a 24 hour time')
        print('Note: If you don\'t enter am/pm, the program assumes 24 hour time')
        print('Please seperate the hour and minute with a colon (:)')
        print('Example - 3:30pm or 17:20')
        user_input = input()

        ## ----- Use regex to pull out time
        pattern = re.compile(r"""
            (\d?\d)             # Hour, not accepting the 0 in front if there
            [:;]                # Time seperator
            (\d?\d)             # Minute, not accpting a 0
            \s*                 # White space is acceptable if it's there
            (am|pm)?            # Matches an am/pm, if there, to determine am/pm time or 24-hour
            """, re.VERBOSE)
        time = pattern.search(user_input.lower())
        # Make sure the regex pulled a valid time
        if time == None:
            cm.clear_screen()
            print('Sorry, that value')
            print(user_input)
            print('Is not a recognizeable time.')
            print('Please make sure to use a colon (:) or enter the time in a different format')
            print()
            continue
        # Seperate regex, make hour and minute strings ints
        hour = int(time.group(1))       # making it an int also removes any preceeding 0's
        minute = int(time.group(2))     # making it an int also removes any preceeding 0's
        am_pm = time.group(3)
        
        ## ----- Clean up the numbers so they make sense
        # Note: Because of the regex, nothing can be negative
        # Clean up the hour
        if am_pm != None and (hour >= 13 or hour == 0): # The user gave an am/pm time and the hours are outside of possible values
            cm.clear_screen()
            print('There are only 12 hours in a day with am/pm.')
            print('There is no 0 hour with am/pm')
            print('Please enter a valid hour.')
            print()
            continue
        elif am_pm == None and hour >= 24: # The user gave an 24-hour time and the hours are outside of possible values
            cm.clear_screen()
            print('There are only 24 hours in a day.')
            print('The clock does not strike hour 24.')
            print('Please enter a valid hour.')
            print()
            continue
        # Clean up the minute
        if minute >= 60:
            cm.clear_screen()
            print('There are only 60 minutes in an hour.')
            print('The clock does not strike minute 60.')
            print('Please enter a valid minute.')
            print()
            continue

        ## ----- Use datetime to convert to 24-hour if in am/pm
        if am_pm != None: # Time is in am/pm hours
            # Build out the str to pass into datetime
            time_string = str(hour) + ':' + str(minute) + ' ' + am_pm
            am_pm_time_obj = datetime.strptime(time_string, "%I:%M %p")
            hour_24_time_obj = datetime.strftime(am_pm_time_obj, "%H:%M")
            hour, minute = hour_24_time_obj.split(':')
            hour = str(int(hour)) # Converting to an int and then back to str removes precceding 0's
            minute = str(int(minute)) # Converting to an int and then back to str removes precceding 0's
        else: # Time is in 24-hour
            hour = str(hour)
            minute = str(minute)
        return hour, minute

def get_days_of_week():
    conversion = {'Sun':'0', 'Mon':'1', 'Tue':'2', 'Wed':'3', 'Thu':'4', 'Fri':'5', 'Sat':'6', 'All':'*'}
    while True:
        # Returns the days of the week the program is to run
        print('What day(s) of the week would you like the program to capture the AO3 info?')
        print('(Yes, you can chose multiple specific days)')
        print('Type as many of the following days as you\'d like:')
        print()
        print('Mon, Tue, Wed, Thu, Fri, Sat, Sun, All')
        print()
        print('The recommended answer is "All" to run every day')
        print('Please seperate the days with commas')
        user_input = input().lower()
        pattern = re.compile(r'(mon|tue|wed|thu|fri|sat|sun|all)')
        days = pattern.findall(user_input)
        print()

        # Make sure something was identified
        if len(days) == 0:
            print('No days were recognized from')
            print(user_input)
            print('Please make sure the days or All are/is spelled appropriately')
            print('If you don\'t want the AO3 fics to be tracked any day of the week, delete all of the jobs instead.')
            continue
        
        # Process the days
        days = [day[0].upper() + day[1:] for day in days] # Capitalizes the firse letter of every word
        days = list(set(days)) # Removes doubles
        days.sort(key=lambda day: conversion[day])
        if 'All' in days or days == ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            return '*'
        else:
            print('Did all the days you wanted get captured? The program identified the following days')
            print(', '.join(days))
            print('Type "Yes" if you\'re satisfied')
            if input().lower().startswith('y'):
                days = [conversion[day] for day in days]
                return ','.join(days)
            else:
                continue
    return None

def add_job(cron):
    while True:
        # Adds an AO3 job and makes sure it's a valid entry
        hour, minute = get_time()
        print()
        dow = get_days_of_week()
        print()
        job = cron.new(command=AO3_cron_command)
        job.setall(minute, hour, '*', '*', dow)
        if not job.is_valid():
            cron.remove(job)
            cm.clear_screen()
            print("I'm sorry, that job isn't valid for some reason.")
            print('It could be because the AO3 script the program runs was deleted.')
            print('Please try again.')
            continue
        return None

def remove_job(cron, jobs):
    # Removes an AO3 job and makes sure it's what the user wants
    while True:
        print_AO3_jobs(jobs)
        print()
        print('Which job would you like to remove?')
        print('Type in the index (or "Cancel" to back out)')
        command = input()
        if command.lower().startswith('c'):
            return None
        elif cm.isPosInt(command) and int(command) < len(jobs):
            print(f'Are you sure you want to remove {command}?')
            print('Type "Yes" or "No"')
            if input().lower().startswith('y'):
                cron.remove(jobs[int(command)])
                return None
            else:
                continue
        else:
            cm.clear_screen()
            print(f'"{command}" is not a valid option. Please try again.')
            print()
            continue
    return None

def change_job_time(cron, jobs):
    # Changes the job and makes sure it's valid
    while True:
        print_AO3_jobs(jobs)
        print()
        print('Which job would you like to change?')
        print('Type in the index (or "Cancel" to back out)')
        command = input()
        if command.lower().startswith('c'):
            return None
        elif cm.isPosInt(command) and int(command) < len(jobs):
            print(f'Are you sure you want to change {command}?')
            print('Type "Yes" or "No"')
            if input().lower().startswith('y'):
                print()
                cron.remove(jobs[int(command)])
                add_job(cron)
                return None
            else:
                continue
        else:
            cm.clear_screen()
            print('That was not a valid option. Please try again.')
            print()
            continue
    return None

def remove_duplicate_jobs(cron, AO3_jobs):
    singles = list() # Used to keep track of what has already been seen
    for job in AO3_jobs:
        if job not in singles:
            singles.append(job)
        else: # job is in singles already, this job is a duplicate and can be deleted
            cron.remove(job)
            # This updates the cron object. AO3_jobs will be updated outside of this function
    return None

def interact_with_cron():
    # Initialize cron interaction
    cron = CronTab(user=True)
    AO3_jobs = get_AO3_jobs(cron)

    # Begin user interaction
    cm.clear_screen()
    while True:
        print('What would you like to do? After typing, hit Enter')
        print('View update times:                    Type "View"')
        print('Add an update time:                   Type "Add"')
        print('Remove an update time:                Type "Remove"')
        print('Change an update time:                Type "Change"')
        print('                   ~~~~~~~~~~             ')
        print('Save your time changes:               Type "Save"')
        print('Quit without saving time changes:     Type "Quit"')
        user_action = input()
        if user_action.lower().startswith(('r', 'c')) and len(AO3_jobs) == 0:
            cm.clear_screen()
            print('There are no current times AO3 data is being collected.')
            print()
            continue
        elif user_action.lower().startswith('v'): # View jobs
            cm.clear_screen()
            print_AO3_jobs(AO3_jobs)
            print()
        elif user_action.lower().startswith('a'): # Add a job
            cm.clear_screen()
            add_job(cron)
            AO3_jobs = get_AO3_jobs(cron)
            cm.clear_screen()
        elif user_action.lower().startswith('r'): # Remove a job
            cm.clear_screen()
            remove_job(cron, AO3_jobs)
            AO3_jobs = get_AO3_jobs(cron)
            cm.clear_screen()
        elif user_action.lower().startswith('c'): # Change a job
            cm.clear_screen()
            change_job_time(cron, AO3_jobs)
            AO3_jobs = get_AO3_jobs(cron)
            cm.clear_screen()
        elif user_action.lower().startswith('s'): # Save the changes and exit
            cm.clear_screen()
            print('Please allow the program to make changes / administer your computer')
            print('It\'s only to add the auto-running to your crontab :)')
            cron.write()
            """
            for job in cron:
                print(job)
            """
            return None
        elif user_action.lower().startswith('q'): # Quit the program
            return None
        else:
            cm.clear_screen()
            print(f"Command not identified - '{user_action}'")
            print('Please re-enter your command')
            continue

        # Add a check to see if two jobs exist with the same time. Delete the duplicate automatically if so
        remove_duplicate_jobs(cron, AO3_jobs)
        AO3_jobs = get_AO3_jobs(cron)
    return None
    
if __name__ == '__main__':
    interact_with_cron()
