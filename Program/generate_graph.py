#!/usr/bin/env python3
import common as cm
import os
import pickle
import datetime
import matplotlib.pyplot as plt
import AO3
import warnings

def generate_graph(workID, ficName, graphDirectory, workHistoryDirectory):
    """
    update_AO3_stats_on - Used for collecting information from AO3, saving that data, and the outputting a graph of that data 

    Author: Fixationally_Consumed

    -------------- Inputs 
    workID (int): The ID number that AO3 uses to reference the work. Can be found in the fic's URL.
                If the URL for the fic is https://archiveofourown.org/works/32751484/chapters/81257581
                then the work ID is 32751484.

    plotTitle (str): Title on the graph, not the filename. I have an engineering background and was shamed (not really) if I didn't put titles on my graphs. It's a habit.
    figureFileName (str): The name of the graph's file. I recommend using the name of your fic. The extension is not required.
    figureDirectory (str): Save location of the graph. EX: Users/Fix/Desktop

    workHistoryDirectory (str): Save location of the data file. This is updated automatically by the code.
    workHistoryFileName (str): The name for the specific save file. I recommend using the name of your fic.

    -------------- Outputs
    Save file: This is the "workHistory" file where all the data is saved. It is a pickle file.
    Graph: Visual depiction of the save file. It's a graph with three subplots, unless altered by the user.

    -------------- Running the script
    This script should be run periodically (I do it daily) to collect data. If you don't want to do it manually, which
    is recommended, use your computer's tools. Mac has crontab (or there's probably something better) to automatically
    run scripts. I'm sure Linux and Windows have their own auto running programs. Whatever the case, just know that
    downloading this script does not mean it will run on it's own.
    """
    # Define Constants -------------------------------------------------------------------
    ## AO3 Work Information
    # workID is passed in
    
    ## ----- Graph/Figure info
    plotTitle = f'"{ficName}" Data' # Title name of the plot
    figureFileName = cm.make_graph_filename(ficName) # Name of the figure, doesn't require file extension
    figureSavePath =  os.path.join(graphDirectory, figureFileName) # Where to save the graph

    ## ----- Data file info
    workHistoryFileName = cm.make_workHistory_filename(ficName, workID)
    workHistorySavePath = os.path.join(workHistoryDirectory, workHistoryFileName) # Where to save the data file for the work

    # Start script -----------------------------------------------------------------
    warnings.filterwarnings(action='ignore', category=UserWarning, module='AO3') # Suppress the annoying UserWarning that some fics may be long in length
    work = AO3.Work(workID)  # Obj. of the AO3 work in its current state.
    publish_date = work.date_published.date()
    todaysDate = datetime.date.today()
    daysSincePublished = (todaysDate - publish_date).days

    # Updating information ---------------------------------------------------------
    if os.path.isfile(workHistorySavePath): # If there is already a previous data save
        with open(workHistorySavePath, "rb") as pFile: # Loading the previously recorded data
            workHistory = pickle.load(pFile)

        if workHistory['days since published'][-1] == daysSincePublished:
            # If the last days since published is the same as todays, don't make a new data point but rather update todays data point
            workHistory['nchapters'][-1] = work.nchapters
            workHistory['kudos'][-1] = work.kudos
            workHistory['ncomments'][-1] = work.comments
            workHistory['hits'][-1] = work.hits
            workHistory['word count'][-1] = work.words
            workHistory['days since published'][-1] = daysSincePublished
            workHistory['chapter added'][-1] = workHistory['nchapters'][-1] !=  workHistory['nchapters'][-2]
            """The above creates a bool flag (I think that's what it's called) for when a new chapter has been posted.
                It checks for a difference between total chapter numbers and returns True if there is.
                This is used to post chapter numbers on the graph when they occur. I used this because the program/AO3
                only keep track of the current state of a fic, and so I had to find a way when the chapter numbers changed.
                This might not be the 'best' way, but it works!"""
        else:
            # Updating the data with a new data point for the current state of the AO3 work    
            workHistory['nchapters'].append(work.nchapters)
            workHistory['kudos'].append(work.kudos)
            workHistory['ncomments'].append(work.comments)
            workHistory['hits'].append(work.hits)
            workHistory['word count'].append(work.words)
            workHistory['days since published'].append(daysSincePublished)
            workHistory['chapter added'].append(workHistory['nchapters'][-1] !=  workHistory['nchapters'][-2])
            """The above creates a bool flag (I think that's what it's called) for when a new chapter has been posted.
                It checks for a difference between total chapter numbers and returns True if there is.
                This is used to post chapter numbers on the graph when they occur. I used this because the program/AO3
                only keep track of the current state of a fic, and so I had to find a way when the chapter numbers changed.
                This might not be the 'best' way, but it works!"""

        with open(workHistorySavePath, 'wb') as pFile: # Saving the updated information
            pickle.dump(workHistory, pFile)
    else: # If there is no previous data. This is only for new runs.
        # Initiate workHistory with a double set of values.
        #   This is so that the 'chapter added' value always has at least two values to compare.
        workHistory = {
            'nchapters': [work.nchapters, work.nchapters,],
            'kudos': [work.kudos, work.kudos,],
            'ncomments': [work.comments, work.comments,],
            'hits': [work.hits, work.hits,],
            'word count': [work.words, work.words,],
            'days since published': [daysSincePublished, daysSincePublished,],
            'chapter added': [True, False,]
        }
        with open(workHistorySavePath, 'wb') as pFile: # Saving the data
            pickle.dump(workHistory, pFile)

    # Generate plot(s) ---------------------------------------------------------
    """
    What I want to plot: days since posted vs _____
       - hits
       - kudos
       - number of comments
     Extra detail in plots
       - Indicate when a new chapter was posted by placing chapter number in chart on the corosponding day
     Side box information
       - Current hit count
       - Current chapter count
       - How many total words are in the work
    """
    ## ----- Plot data and label axes
    fig, (ax_hits, ax_kudos, ax_ncomments) = plt.subplots(3, 1, figsize=(15,15))

    ax_hits.plot(workHistory['days since published'], workHistory['hits'])
    ax_hits.set_xlabel('Days since Published') ; ax_hits.set_ylabel('Hits', fontsize=25)

    ax_kudos.plot(workHistory['days since published'], workHistory['kudos'])
    ax_kudos.set_xlabel('Days since Published') ; ax_kudos.set_ylabel('Kudos', fontsize=25)

    ax_ncomments.plot(workHistory['days since published'], workHistory['ncomments'])
    ax_ncomments.set_xlabel('Days since Published') ; ax_ncomments.set_ylabel('Comments', fontsize=25)

    ## ----- Plotting chapter numbers when new chapter is posted (not plotting chapter number for every data point)
    """
    This checks for when a new chapter was detected, which is determined every time the program updates it's data (around line 33).
    Then, the bool list is iterated through, and every time a new chapter was posted the current chapter number is plotted.
    """
    for i, newChapterBool in enumerate(workHistory['chapter added']):
        if newChapterBool is True:
            ax_hits.text(workHistory['days since published'][i], # x-value
                         workHistory['hits'][i], # y-value
                         workHistory['nchapters'][i], fontsize=14) # Text (chapter number)
            
            ax_kudos.text(workHistory['days since published'][i], # x-value
                         workHistory['kudos'][i], # y-value
                         workHistory['nchapters'][i], fontsize=14) # Text (chapter number)
            
            ax_ncomments.text(workHistory['days since published'][i], # x-value
                              workHistory['ncomments'][i], # y-value
                              workHistory['nchapters'][i], fontsize=14) # Text (chapter number)

    ## ----- Creating text box off to the side that displays extra info
    info = 'Hits:         {}\n'.format(workHistory['hits'][-1])  \
         + 'Chapters:  {}\n'.format(workHistory['nchapters'][-1])  \
         + 'Words:       {}\n'.format(workHistory['word count'][-1])
    fig.text(1, .5, info, fontsize=25, ha='left', va='center')

    ## ----- Title plot
    fig.suptitle(plotTitle, fontsize=30)
    plt.tight_layout()
    #plt.show() # Use to show plot while editing. Comment out plt.savefig() if you don't want to write the file yet while editing.
    plt.savefig(figureSavePath, dpi=300, bbox_inches = "tight")
    return None
