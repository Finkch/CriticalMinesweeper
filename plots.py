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
    if 'expMeta' in results:
        print(etostr(results['expMeta']))
    elif 'cdMetas' in results:  # Prints first and last
        print(etostr(results['cdMetas'][0]))
        print(etostr(results['cdMetas'][-1]))

    graph.histogram(
        reveals = results['expReveals'],
        params = results['expMeta']
    )


# Compares the critical density for starting areas of differing radius
def is_start_rho():

    dir = 'IsStartRho'

    dir = f'Results/{dir}'

    # Gets the series of experiments
    dirs = os.listdir(dir)

    # Unlogs each
    exps = [unlog(f'{dir}/{exp}') for exp in dirs if exp != '.DS_Store']

    # Shows that CD and initial starting area are unrelated
    graph.show_is_start_rho(
        rhos = {i: exps[i]['cdRhos'][-1] for i in range(len(exps))}
    )

# Compares the growth factor, alpha, for various rhos
def alphas():
    
    dir = 'CoarseAlphas'

    dir = f'Results/{dir}'

    dirs = os.listdir(dir)

    # Grabs each experiment
    exps = [unlog(f'{dir}/{exp}') for exp in dirs if exp != '.DS_Store']

    graph.show_alphas(
        reveals = exps['expReveals'],
        alphas = exps['expAlphas'],
        rhos = [float(exp['expMeta']['rho']) for exp in exps]
    )

# Shows how alpha is proportional to the cutoff.
# The smaller the cutoff, the larger the alpha.
# Here, rho is zero.
def max_alphas():
    
    dir = 'MaxAlphas'

    dir = f'Results/{dir}'

    dirs = os.listdir(dir)

    # Grabs each experiment
    results = [unlog(f'{dir}/{exp}') for exp in dirs if exp != '.DS_Store']

    graph.show_max_alphas(
        alphas = [max(alphas) for alphas in results['expAlphas']], 
        cutoffs = [float(meta['expMeta']['cutoff']) for meta in results]
    )

    


#see_ms()
#histogram()
#is_start_rho()
alphas()
#max_alphas()