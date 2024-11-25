# Runs experiments to find the critical density

from experiment import Experiment

class CriticalDensity:
    def __init__(self, experiments: int, trials: int, rho_initial: float, cutoff_initial: int, step: float, alpha: float) -> None:
        
        # The number of experiments to run
        self.experiments = experiments

        # The number of trials per experiment
        self.trials = trials



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

        # Step size
        self.step = step

        # Alpha is a decay constant
        self.alpha = alpha


        # A list of experimental results
        self.results = []



    # Finds the critical density
    def find(self) -> float:
        
        for experiment in range(self.experiments):

            # Creates a new experiment
            exp = Experiment(self.rho, self.cutoff, self.trials)

            # Runs the experiment
            result = exp.begin()

            # Adds the experiment's results
            self.results.append(result)


            # Determines the step size
            if result['infinite']:
                
                # Step size is proportional to how quickly the board went infinite
                s = result['trials'] / result['goal']

            else:

                # Step size is proportional to how far it got to being infinite
                # I'll need to play around with this one
                s = result['max'] / result['cutoff']

            self.rho += s

            # Decreases step size exponentially
            self.step *= self.alpha

