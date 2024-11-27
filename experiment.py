# Experiment is a series of trials at a given density

from minesweeper import Minesweeper

from math import ceil


class Experiment:
    def __init__(self, rho: float, cutoff: int, trials: int, do_cutoff: bool = True) -> None:
        self.rho = rho
        self.cutoff = cutoff
        self.trials = trials

        self.do_cutoff = do_cutoff

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

            if not quiet and trial % 10 == 0:
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

        results['str'] = str(self)

        return results


    def __str__(self) -> str:

        s = 'Experiment results: valid density.\n' if len(self.results) == self.trials else 'Experiment results: INFINTIE.\n'

        s += f'.. Trials:\t\t{len(self.results)}\n'
        s += f'.. Density:\t\t{self.rho}\n'
        s += f'.. Cutoff:\t\t{self.cutoff}\n'
        s += f'.. Average reveals:\t{sum(self.results) / len(self.results)}\n'
        s += f'.. Median reveals: \t{self.results[len(self.results) // 2]}\n'
        s += f'.. Minimum reveals:\t{self.results[0]}\n'
        s += f'.. Maximum reveals:\t{self.results[-1]}\n'

        return s

