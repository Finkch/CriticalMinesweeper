# An alternative execution path to show the results of various experiments


from experiment import etostr
from minesweeper import Minesweeper

import graph
from logger import unlog
from visualise import visualise, pygame_init

import os
import numpy as np


# Execution path to visualise a given trial
def see_ms():

    rho = 0.1
    cutoff = 1000

    ms = Minesweeper(rho, cutoff, True)
    ms.sweep()

    pygame_init()
    visualise(ms)

# Draws a histogram of reveals at a given density
def histogram():
    
    dir = '5x7rho0-1'

    # Obtains the results from file
    results = unlog(f'Results/{dir}')

    # Performs a printout of the parameters
    if 'compressede' in results:
        print(etostr(results['compressede']))
    elif 'compressedc' in results:  # Prints first and last
        print(etostr(results['compressedc'][0]))
        print(etostr(results['compressedc'][-1]))

    graph.histogram(results)


# Compares the critical density for starting areas of differing radius
def is_start_rho():

    dir = 'IsStartRho'

    dir = f'Results/{dir}'

    # Gets the series of experiments
    dirs = os.listdir(dir)

    # Unlogs each
    exps = [unlog(f'{dir}/{exp}') for exp in dirs if exp != '.DS_Store']

    # Grabs the results we care about.
    # That is the final value found, i.e. the CD Finder's found CD
    results = [exp['rhosc'][-1] for exp in exps]

    # Finds the average rho and its error
    mean = np.mean(results)
    se = np.std(results) / np.sqrt(len(results))
    
    print(f'Mean critical density over r = [0, 9]:\n.. {graph.sigfigs(mean, se)}')
    


#see_ms()
#histogram()
is_start_rho()