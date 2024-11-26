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

def main():
    
    experiments = int(1e2)
    trials = int(1e3)
    rho = 3 / 5
    cutoff = 1e5
    step = 0.3
    alpha = 0.65

    finder = CriticalDensity(experiments, trials, rho, cutoff, step, alpha)

    print(finder.find(False))


main()