# Experiment is a series of trials at a given density

from minesweeper import Minesweeper

from math import ceil

from logger import log


class Experiment:
    def __init__(self, rho: float, cutoff: int, trials: int, do_cutoff: bool = True, r: int = 1, logdir: str = None) -> None:
        self.rho = rho
        self.cutoff = cutoff
        self.trials = trials
        self.r = r

        self.do_cutoff = do_cutoff

        self.logdir = logdir

        self.results = []
        self.alphas = []


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
            board = Minesweeper(self.rho, self.cutoff, self.r)

            # Runs a trial
            alpha = board.sweep()

            # Appends the results
            self.results.append(board.reveals)
            self.alphas.append(alpha)

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
        self.alphas.sort()

        results = {}

        results['infinite'] = self.results[-1] == self.cutoff
        results['goal']     = self.trials
        results['trials']   = len(self.results)
        results['rho']      = self.rho
        results['cutoff']   = self.cutoff
        results['safe']     = self.r
        results['mean']     = sum(self.results) / len(self.results)
        results['median']   = self.results[len(self.results) // 2]
        results['min']      = self.results[0]
        results['max']      = self.results[-1]
        results['amean']    = sum(self.alphas) / len(self.alphas)
        results['amedian']  = self.alphas[len(self.alphas) // 2]
        results['amin']     = self.alphas[0]
        results['amax']     = self.alphas[-1]
        results['infinites']= sum([1 for result in self.results if result == self.cutoff])

        # Logs the experiment
        if self.logdir:
            log(self.logdir, 'fulle', self.results)
            log(self.logdir, 'alphase', self.alphas)
            log(self.logdir, 'compressede', results)

        return results


    def __str__(self) -> str:

        # Grabs the data
        results = self.process()

        s = 'Experiment results: valid density.\n' if not results['infinite'] else 'Experiment results: INFINTIE.\n'

        s += f'.. Trials:\t\t{results["trials"]} of {results["goal"]}\n'
        s += f'.. Density:\t\t{results["rho"]}\n'
        s += f'.. Cutoff:\t\t{results["cutoff"]}\n'
        s += f'.. Safe Radius:\t\t{results["safe"]}\n'
        s += f'.. Average reveals:\t{results["mean"]}\t({results["mean"] / results["cutoff"] * 100:.2f}%)\n'
        s += f'.. Median reveals: \t{results["median"]}\t({results["median"] / results["cutoff"] * 100:.2f}%)\n'
        s += f'.. Count of infinities:\t{results["infinites"]}\t({results["infinites"] / results["trials"] * 100:.2f}%)\n'
        s += f'.. Minimum reveals:\t{results["min"]}\n'
        s += f'.. Maximum reveals:\t{results["max"]}\n'
        s += f'.. Average alpha:\t{results["amean"]:.2f}\n'
        s += f'.. Median alpha:\t{results["amedian"]:.2f}\n'
        s += f'.. Minimum alpha:\t{results["amin"]:.2f}\n'
        s += f'.. Maximum alpha:\t{results["amax"]:.2f}\n'

        return s


# Used to reformat experimental results into a string
def etostr(results):

    s = 'Experiment results: valid density.\n' if not bool(results['infinite']) else 'Experiment results: INFINTIE.\n'

    s += f'.. Trials:\t\t{results["trials"]} of {results["goal"]}\n'
    s += f'.. Density:\t\t{results["rho"]}\n'
    s += f'.. Growth Factor:  \t{results["alpha"]}\n'
    s += f'.. Cutoff:\t\t{results["cutoff"]}\n'
    s += f'.. Safe Radius:\t\t{results["safe"]}\n'
    s += f'.. Average reveals:\t{results["mean"]}\t({float(results["mean"]) / float(results["cutoff"]) * 100:.2f}%)\n'
    s += f'.. Median reveals: \t{results["median"]}\t({float(results["median"]) / float(results["cutoff"]) * 100:.2f}%)\n'
    s += f'.. Count of infinities:\t{results["infinites"]}\t({float(results["infinites"]) / float(results["trials"]) * 100:.2f}%)\n'
    s += f'.. Minimum reveals:\t{results["min"]}\n'
    s += f'.. Maximum reveals:\t{results["max"]}\n'
    s += f'.. Average alpha:\t{results["amean"]}\n'
    s += f'.. Median alpha:\t{results["amedian"]}\n'
    s += f'.. Minimum alpha:\t{results["amin"]}\n'
    s += f'.. Maximum alpha:\t{results["amax"]}\n'

    return s
