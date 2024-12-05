# Experiment is a series of trials at a given density

from minesweeper import Minesweeper

from math import ceil

from logger import log


class Experiment:
    def __init__(self, rho: float, cutoff: int, trials: int, do_cutoff: bool = True, logdir: str = None) -> None:
        self.rho = rho
        self.cutoff = cutoff
        self.trials = trials

        self.do_cutoff = do_cutoff

        self.logdir = logdir

        self.results = []


    # Starts the experiment
    def begin(self, quiet = True) -> dict:

        if not quiet:
            print(f'Beginning experiment:')
            print(f'.. Trials:\t{self.trials}')
            print(f'.. Density:\t{self.rho}')
            print(f'.. Cutoff:\t{self.cutoff}')
        
        # Performs the experiment
        for trial in range(self.trials):

            # Creates new board
            board = Minesweeper(self.rho, self.cutoff)

            # Runs a trial
            board.sweep()

            # Appends the results
            self.results.append(board.reveals)

            # Stops the experiment if a board ever goes infinite
            if board.reveals >= self.cutoff and self.do_cutoff:
                break

            if not quiet and trial % (self.trials // 10) == 0:
                print(f'{ceil(trial / self.trials * 100)}%')


        if not quiet:
            print(f'100%')
            print(f'Experimetn concluded.\n\n')

        # Returns a compressed set of results
        return self.process()


    # Compresses the results
    def process(self) -> dict:

        self.results.sort()

        results = {}

        results['infinite'] = len(self.results) < self.trials
        results['goal']     = self.trials
        results['trials']   = len(self.results)
        results['rho']      = self.rho
        results['cutoff']   = self.cutoff
        results['mean']     = sum(self.results) / len(self.results)
        results['median']   = self.results[len(self.results) // 2]
        results['min']      = self.results[0]
        results['max']      = self.results[-1]
        results['infinites']= sum([1 for result in self.results if result == self.cutoff])

        # Logs the experiment
        if self.logdir:
            log(self.logdir, 'full', self.results)
            log(self.logdir, 'compressed', results)

        return results


    def __str__(self) -> str:

        # Grabs the data
        results = self.process()

        s = 'Experiment results: valid density.\n' if not results['infinite'] else 'Experiment results: INFINTIE.\n'

        s += f'.. Trials:\t\t{results["trials"]} of {results["goal"]}\n'
        s += f'.. Density:\t\t{results["rho"]}\n'
        s += f'.. Cutoff:\t\t{results["cutoff"]}\n'
        s += f'.. Average reveals:\t{results["mean"]}\t({results["mean"] / results["cutoff"] * 100:.2f}%)\n'
        s += f'.. Median reveals: \t{results["median"]}\t({results["median"] / results["cutoff"] * 100:.2f}%)\n'
        s += f'.. Count of infinities:\t{results["infinites"]}\t({results["infinites"] / results["trials"] * 100:.2f}%)\n'
        s += f'.. Minimum reveals:\t{results["min"]}\n'
        s += f'.. Maximum reveals:\t{results["max"]}\n'

        return s

