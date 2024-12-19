# Experiment is a series of trials at a given density

#from minesweeper import Minesweeper
from minesweeperp import minesweeper

from math import ceil

from logger import log

import signal

def timeout_handler(signum, frame):
    raise TimeoutError('Operation timed out.')


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

        signal.signal(signal.SIGALRM, timeout_handler)


    # Starts the experiment
    def begin(self, quiet = True) -> dict:

        if not quiet:
            print(f'Beginning experiment:')
            print(f'.. Trials:\t{self.trials}')
            print(f'.. Density:\t{self.rho}')
            print(f'.. Cutoff:\t{self.cutoff}')


        # Performs the experiment
        for trial in range(self.trials):            

            try:

                # Primes alarm
                signal.alarm(60)

                # Creates new board
                #board = Minesweeper(self.rho, self.cutoff, self.r)

                # Runs a trial
                reveals, sizes = minesweeper(self.rho, self.r, self.cutoff ** 0.5)

                # Appends the results
                self.results.append(reveals)
                self.alphas.append(sizes.tolist())

                # Disables alarm
                signal.alarm(0)
            
            # Crash anyways so I can see what happened
            except TimeoutError:
                raise TimeoutError(f'Oh, stars! Have been sweeping mines for too long!')
            
            # Ensures alarm is deactivated
            finally:
                signal.alarm(0)


            # Stops the experiment if a board ever goes infinite
            if reveals >= self.cutoff and self.do_cutoff:
                break

            if not quiet and self.trials // 10 > 0 and trial % (self.trials // 10) == 0:
                print(f'{ceil(trial / self.trials * 100)}%')


        if not quiet:
            print(f'100%')
            print(f'Experimetn concluded.\n\n')

        # Returns a compressed set of results
        return self.process()


    # Compresses the results
    def process(self) -> dict:

        try:

            # Primes alarm
            signal.alarm(10)

            # A list of experimentally determined reveals, alphas packed together
            reveals = self.results
            alphas = self.alphas

            # Metadata of the experimental parameters
            meta = {
                'goal':     self.trials,
                'trials':   len(self.results),
                'rho':      self.rho,
                'cutoff':   self.cutoff,
                'd':        self.r,
                'max':      max(self.results),
                'min':      min(self.results),
                'mean':     sum(self.results) / len(self.results),
                'infinite': max(self.results) == self.cutoff
            }

            if len(alphas) > 0 and not isinstance(alphas[0], list):
                meta['amin'] = min(self.alphas)
                meta['amax'] = max(self.alphas)
                meta['amean'] = sum(self.alphas) / len(self.alphas),

            # Logs the experiment
            if self.logdir:
                log(self.logdir, 'expReveals', reveals)
                log(self.logdir, 'expMeta', meta)

                if len(alphas) > 0:
                    log(self.logdir, 'expAlphas', alphas)

            # Disables alarm
            signal.alarm(0)

        # Crash anyways so I can see what happened
        except TimeoutError:
            raise TimeoutError(f'Oh, change! Ran into issue logging results!')
        
        # Ensures alarm is deactivated
        finally:
            signal.alarm(0)

        return reveals, alphas, meta


    def __str__(self) -> str:

        mean = sum(self.results) / len(self.results)
        #amean = sum(self.alphas) / len(self.alphas)

        s = 'Experiment results: valid density.\n' if max(self.results) < self.cutoff else 'Experiment results: INFINTIE.\n'

        s += f'.. Trials:\t\t{len(self.results)} of {self.trials}\n'
        s += f'.. Density:\t\t{self.rho}\n'
        s += f'.. Cutoff:\t\t{self.cutoff}\n'
        s += f'.. Safe Radius:\t\t{self.r}\n'
        s += f'.. Average reveals:\t{mean}\t({mean / self.cutoff * 100:.2f}%)\n'
        s += f'.. Minimum reveals:\t{min(self.results)}\n'
        s += f'.. Maximum reveals:\t{max(self.results)}\n'
        # s += f'.. Average alpha:\t{amean:.2f}\n'
        # s += f'.. Minimum alpha:\t{min(self.alphas):.2f}\n'
        # s += f'.. Maximum alpha:\t{max(self.alphas):.2f}\n'

        return s


# Used to reformat experimental results into a string
def etostr(meta):

    s = 'Experiment results: valid density.\n' if not bool(meta['infinite']) else 'Experiment results: INFINTIE.\n'

    s += f'.. Trials:\t\t{meta["trials"]} of {meta["goal"]}\n'
    s += f'.. Density:\t\t{meta["rho"]}\n'
    s += f'.. Cutoff:\t\t{meta["cutoff"]}\n'
    s += f'.. Safe Radius:\t\t{meta["d"]}\n'
    s += f'.. Average reveals:\t{meta["mean"]}\t({float(meta["mean"]) / float(meta["cutoff"]) * 100:.2f}%)\n'
    s += f'.. Minimum reveals:\t{meta["min"]}\n'
    s += f'.. Maximum reveals:\t{meta["max"]}\n'
    s += f'.. Average alpha:\t{meta["amean"]}\n'
    s += f'.. Minimum alpha:\t{meta["amin"]}\n'
    s += f'.. Maximum alpha:\t{meta["amax"]}\n'

    return s
