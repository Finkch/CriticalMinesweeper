# A program to answer a single questions:
# On an infinite board, what is the critical density of mines such that
# the initial reveal is finite?
#
# According to ChatGPT, which says according to percolation theory, the answer is about pho = 0.59.
# I prefer my coffee drip brewed, so let's find out experimentally.
#       Wow...that was a bad joke.

from experiment import Experiment

def main():
    
    trials = int(1e2)
    rho = 3 / 5
    cutoff = 1e5

    exp: Experiment = Experiment(rho, cutoff, trials)

    exp.begin(quiet = False)

    print(exp)
    


main()