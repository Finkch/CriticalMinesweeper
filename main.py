# A program to answer a single questions:
# On an infinite board, what is the critical density of mines such that
# the initial reveal is finite?
#
# According to ChatGPT, which says according to percolation theory, the answer is about pho = 0.59.
# I prefer my coffee drip brewed, so let's find out experimentally.
#       Wow...that was a bad joke.
#
# First real simulation has finished!

# Todo:
#   * Get trials to cutoff early if they are very confident they are not infinite
#   * Improve CDFinder end condition
#   *   - End when step is sufficiently small?
#   *   - End when deviation between last n experiments is sufficiently small?
#   * Think about deltas in experiment: don't cutoff early when infinite, rather delta proportional to #infinite?
#   * Add another bit (or repurpose 1) to code if cell in in RQ to avoid lengthy 'in' check
#   * Write key results to file 
#   * Make graphs of reveals vs. density
#       - Reveals vs. density (trial)
#       - Mean/median reveals vs. density (experiment)
#       - Max reveals vs. density (experiment)
#       - Phase diagram cutoff vs. trials (CD finer)

from critical import CriticalDensity
from experiment import Experiment

from time import time

# Performs many experiment to find critical density
def main():
    
    experiments = int(1e2)
    trials = int(1e3)
    rho = 3 / 5
    cutoff = 1e5
    step = 0.3
    alpha = 0.65

    finder = CriticalDensity(experiments, trials, rho, cutoff, step, alpha)

    print(finder.find(False))

# Performs an experiment to figure out its speed
def performance():
    
    trials = int(1e3)
    rho = 0.05      # Roughly rho_critical / 2. More or less guarantees infinite reveal
    cutoff = 1e5

    experiments = 10

    results = []

    for experiment in range(experiments):

        print(f'Starting experiment {experiment + 1}...')

        # Experiment setup
        exp = Experiment(rho, cutoff, trials)

        # Runs a trial
        start = time()

        exp.begin()

        end = time()

        # Experiment end
        results.append(end - start)

    results.sort()

    print(f'\nExperiment concluded:')
    print(f'.. Mean time:\t{sum(results) / len(results):.4f}s')
    print(f'.. Median time:\t{results[len(results) // 2]:.4f}s')
    print(f'.. Minimum time:\t{results[0]:.4f}s')
    print(f'.. Maximum time:\t{results[-1]:.4f}s')




#main()
performance()