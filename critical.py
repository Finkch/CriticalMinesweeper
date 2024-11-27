# Runs experiments to find the critical density

from experiment import Experiment

from time import time

class CriticalDensity:
    def __init__(self, experiments: int, trials: int, rho_initial: float, cutoff_initial: int, do_cutoff: bool, step: float, alpha: float, lastn: int, finder_cutoff: float) -> None:
        
        # The number of experiments to run
        self.experiments = experiments

        # The number of trials per experiment
        self.trials = trials

        # Whether to end trials early
        self.do_cutoff = do_cutoff


        # Starting values.
        # This wil change after each experiment to hone
        self.rho_initial = rho_initial
        self.cutoff_initial = cutoff_initial

        # Current values
        self.rho = rho_initial
        self.cutoff = cutoff_initial



        # After each experiment, rho and cutoff changes depending on experimental results.
        # However, each trial the change will get relatively smaller proportional to alpha.
        # The inital step size is determined by the step value.

        # Maximum step size
        self.step = step

        # Alpha is a decay constant
        self.alpha = alpha



        # When to stop the finder
        self.finder_cutoff = finder_cutoff

        # How many previous experiments to consider for the finder cutoff
        self.lastn = lastn 


        # A list of experimental results
        self.results = []
        self.time_results = []
        self.rhos = []



    # Finds the critical density by gradient descent (-ish)
    def find(self, quiet = True) -> float:
        
        for experiment in range(self.experiments):

            # Breaks if there is a negligible change
            if self.deltas(experiment):
                break


            if not quiet:
                print(f'Beginning experiment {experiment} of {self.experiments}:')

            # Creates a new experiment
            exp = Experiment(self.rho, self.cutoff, self.trials, self.do_cutoff)

            # Runs the experiment
            start = time()
            result = exp.begin()
            end = time()

            # Adds the experiment's results
            self.results.append(result)
            self.time_results.append(end - start)
            self.rhos.append(self.rho)


            # Determines the step size
            if result['infinite']:
                
                # Step size is proportional to how quickly the board went infinite.
                # The faster the infinite, the greater the change
                s = 1 - result['trials'] / result['goal']

            else:

                # Step size is proportional to how close it got to being infinite.
                # The closer to infinite, the smaller the change.
                # Negative value since we want rho to decrease
                # I'll need to play around with this one
                s = result['max'] / result['cutoff'] - 1

            # Updates density
            delta = s * self.step


            # Prints experiment results
            if not quiet:
                print(f'.. Step percent:\t{abs(s):.4f}')
                print(f'.. Current step:\t{self.step:.4f} -> {self.step * self.alpha:4f}')
                print(f'.. Density:\t\t{self.rho:.4f} -> {self.rho + delta:.4f} ({delta:+.4f})')
                print(f'.. Time taken:\t\t{end - start:.4f}s')
                print(exp)

            self.rho += delta

            # Decreases step size exponentially
            self.step *= self.alpha

        self.time_results.sort()

        # The equilibrium value
        return self.rho


    def str_time(self):
        return f"""
Performance data:
.. Mean time:\t\t{sum(self.time_results) / len(self.time_results):.4f}s
.. Median time:\t\t{self.time_results[len(self.time_results) // 2]:.4f}s
.. Minimum time:\t{self.time_results[0]:.4f}s
.. Maximum time:\t{self.time_results[-1]:.4f}s
"""

    # Check if there has been minimal change over the past few trials
    def deltas(self, experiment):

        if experiment > self.lastn:

            # Gets the difference between the extremal elements
            rhos = self.rhos[experiment - self.lastn:]
            maxdelta = max(rhos) - min(rhos)

            # Returns whether the largest change is very small
            if maxdelta < self.finder_cutoff:

                print(f'\Critical density found; no significant change in delta: ±{maxdelta:.3e}.\n')
                return True
            
            print(f'\nContinuing; sufficient change in delta: ±{maxdelta:.3e}.\n')
            return False
