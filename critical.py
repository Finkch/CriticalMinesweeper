# Runs experiments to find the critical density

from experiment import Experiment

from time import time

from logger import log



# Various methods to find what the step out to be


# Do nothing
def stasis(self, meta: dict) -> tuple[float]:
    return self.rho, 0, 0, 1

# The default.
#   Step up based on how close max was to cutoff.
#   Step down based on how few trials before the cutoff.
def half_gradient(self, meta: dict) -> tuple[float]:
    
    # Determines the step size
    if meta['infinite']:
        
        # Step size is proportional to how quickly the board went infinite.
        # The faster the infinite, the greater the change
        s = 1 - meta['trials'] / meta['goal']

    else:

        # Step size is proportional to how close it got to being infinite.
        # The closer to infinite, the smaller the change.
        # Negative value since we want rho to decrease
        # I'll need to play around with this one
        s = meta['max'] / meta['cutoff'] - 1

    # Updates density
    delta = s * self.step

    # Decreases step size exponentially
    step = self.step * self.alpha

    return self.rho + delta, delta, step, s



# This function starts in the infinite case and walks down to CD. Works best with LARGE cutoff
#   Step up never. If exp is non-infinute, do no step and return to previous state but with a smaller step.
#   Step down when trial was infinute. Do not decrease step size.
def down_step(self, meta: dict) -> tuple[float]:
    
    # Used to step back
    if not hasattr(self, 'previous_rho'):
        self.previous_rho = [0]

    # Declarations
    rho     = self.rho
    delta   = 0
    step    = 0
    s       = 0

    if meta['infinite']:

        # This step was infinite, so we're safe to return to it
        self.previous_rho.append(rho)

        s = 1
        step = self.step
        delta = step
        rho = rho + delta
    
    else:
        
        # Return to the previous rho
        rho = self.previous_rho.pop()

        # Decreases step
        step = self.step * self.alpha
        delta = self.rho - rho
        s = -1

    return rho, delta, step, s




class CriticalDensity:
    def __init__(self, experiments: int, trials: int, rho_initial: float, cutoff_initial: int, do_cutoff: bool, r: int, step: float, alpha: float, lastn: int, finder_cutoff: float, stepper: callable = half_gradient, logdir: str = None) -> None:
        
        # The number of experiments to run
        self.experiments = experiments

        # The number of trials per experiment
        self.trials = trials

        # Initial safe zone
        self.r = r

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

        # How to calculate the next rho
        self.stepper = stepper



        # When to stop the finder
        self.finder_cutoff = finder_cutoff

        # How many previous experiments to consider for the finder cutoff
        self.lastn = lastn 


        # A list of experimental results
        self.reveals = []
        self.alphas = []
        self.metas = []
        self.times = []
        self.rhos = []

        # Where to log.
        # If None, then don't log
        self.logdir = logdir



    # Finds the critical density by gradient descent (-ish)
    def find(self, quiet = True) -> float:
        
        for experiment in range(self.experiments):

            # Breaks if there is a negligible change
            if self.lastn > 0 and self.deltas(experiment):
                break


            if not quiet:
                print(f'Beginning experiment {experiment + 1} of {self.experiments}:')

            # Creates a new experiment
            exp = Experiment(self.rho, self.cutoff, self.trials, self.do_cutoff, self.r)

            # Runs the experiment
            start = time()
            reveals, alphas, meta = exp.begin()
            end = time()

            # Adds the experiment's results
            self.reveals.append(reveals)
            self.alphas.append(alphas)
            self.metas.append(meta)
            self.times.append(end - start)
            self.rhos.append(self.rho)

            # Calculates what the next rho should be
            nrho, delta, nstep, s = self.stepper(self, meta)


            # Prints experiment results
            if not quiet:
                print(f'.. Step percent:\t{abs(s):.4f}')
                print(f'.. Current step:\t{self.step:.4f} -> {nstep:4f}')
                print(f'.. Density:\t\t{self.rho:.4f} -> {nrho:.4f} ({delta:+.4f})')
                print(f'.. Time taken:\t\t{end - start:.4f}s')
                print(exp)


            # Updates values
            self.step = nstep
            self.rho = nrho

        if self.logdir:
            log(self.logdir, 'cdTimes', self.times)
            log(self.logdir, 'cdRhos',  self.rhos)
            log(self.logdir, 'cdReveals', self.reveals)
            log(self.logdir, 'cdAlphas', self.alphas)
            log(self.logdir, 'cdMetas', self.metas)

        # The equilibrium value
        return self.rho


    def str_time(self):
        return f"""
Performance data:
.. Total time:\t\t{sum(self.times):.4f}s
.. Mean time:\t\t{sum(self.times) / len(self.times):.4f}s
.. Median time:\t\t{self.times[len(self.times) // 2]:.4f}s
.. Minimum time:\t{self.times[0]:.4f}s
.. Maximum time:\t{self.times[-1]:.4f}s
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
