# An infinite board of minesweeper.

# A cell is a bitflag int E 0, 7.
#   1 = is revealed
#   2 = is mine
#   4 = at least one adjacent mine
#   8 = item has been placed in the reveal queue

from random import random
from random import seed as sseed
from copy import deepcopy
from time import time

# rho is the density of mines, aka p(mine).
# cutoff is the number of reveals before we say "yup, that's an infinite reveal".
# Visualise pushes each step into a queue so we can go over the reveal stepwise later.
# r is the initial safezone radius; 0 -> classic start, 1 -> modern start.
class Minesweeper:
    def __init__(self, rho: float, cutoff: int, r: int = 1, visualise: bool = False, seed: float = None) -> None:
        
        # the number of reveals
        self.reveals: int = 0

        # a queue of which cells to reveal next.
        # this approach allows a radial expansion.
        # Effectively a 1d list of vectors
        self.rq: list[tuple[int]] = []

        # The board grid
        self.grid: dict[tuple[int]] = {}

        # The mine density
        self.rho: float = rho

        # When a reveal is considered infinite
        self.cutoff: int = cutoff

        # Whether to save info for later visualisation
        self.visualise = visualise
        self.grids = []
        self.cells = []
        self.torqs = []

        # Sets random seed
        self.seed = seed if seed else time()
        sseed(self.seed)


        # Starting cell.
        self.rq.append((0, 0))

        # Creates the starting no-mine zone
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):

                # Adds the item to the reveal queue.
                # Not b(0, 0) because we want that to be revealed first
                if not (dx == 0 and dy == 0):
                    self.rq.append((dx, dy))

                # Initialises grid cell
                self.grid[(dx, dy)] = 8
                

    # Does the game of expand
    def sweep(self) -> None:

        # Local variables are faster than attributes!
        grid = self.grid
        rq = self.rq
        cutoff = int(self.cutoff)
        rho = self.rho
        reveals = self.reveals
        visualise = self.visualise

        # Since we're calling this method a tone, faster to make it local
        reveal = self.reveal

        # Tracks the growth factor
        alpha = 0

        # Keeps revealing cells until either the cutoff is reached, or no cells left to reveal
        while reveals < len(rq) and reveals < cutoff:
            alpha += reveal(rq[reveals], grid, rq, rho, visualise)
            reveals += 1

        # Updates value
        self.reveals = reveals

        # Returns growth factor
        return alpha / reveals
    

    # Performs a "single" reveal
    def reveal(self, pos: tuple[int], grid: dict[tuple[int]], rq: list[tuple[int]], rho: float, visualise: bool) -> None:

        # I will likely remove this check once everything is working.
        # This check decreases performance! But only by a hair
        assert not grid[pos] & 3, f"Issue revealing cell b({pos[0]}, {pos[1]}) = {grid[pos]}"


        # Unpacks positions for quick reference
        x, y = pos[0], pos[1]

        # Reaveals the cell
        grid[pos] |= 1

        # Calculates the growth factor of this cell:
        # the number of cells this reveal has added to the torq.
        alpha = 0

        
        # Creates new cells in unoccupied grid positions
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):

                # Gets the new position
                npos = (x + dx, y + dy)

                # Fills unoccupied cells
                if npos not in grid:

                    # 2 means there a mine, 8 is that it's in the to reveal queue
                    grid[npos] = 2 if random() < rho else 0


                # Updates newly revealed cell for is nonzero
                if grid[npos] & 2:
                    grid[pos] |= 4
        

        # Reveals adjacent cells, if self is zero
        if not grid[pos] & 4:        
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):

                    # Gets the new position
                    npos = (x + dx, y + dy)

                    # Neither revealed nor in reveal queue
                    if not grid[npos] & 9:
                        rq.append(npos)
                        grid[npos] |= 8
                        alpha += 1

        # Save data for visualisation later
        if visualise:
            self.grids.append(deepcopy(grid))
            self.cells.append(pos)
            #self.torqs.append(torq if not grid[pos] & 4 else [])

        return alpha


# Following is a list of performance data and the changes relative to old or current.
# The following data was performed in the order listed.
# All trials will be using the following parameters:
#   Experiemnts = 10
#   Trials      = 100
#   Cutoff      = 10000
#   Density     = 0.05
#
# Control (no changes from old):
#   .. Mean time:           27.9167s
#   .. Median time:         28.0180s
#   .. Minimum time:        27.3864s
#   .. Maximum time:        28.2706s
#
# 4th bitflag for has been added to reveal queue
#   .. Mean time:           23.9088s
#   .. Median time:         23.8680s
#   .. Minimum time:        23.6003s
#   .. Maximum time:        24.3395s
#
# 1D grid with tuple coordinates:
#   .. Mean time:           20.4261s
#   .. Median time:         20.4588s
#   .. Minimum time:        19.9676s
#   .. Maximum time:        20.7237s
#
# Precomputed neighbour offset:
#   .. Mean time:           21.4810s
#   .. Median time:         21.5064s
#   .. Minimum time:        21.1753s
#   .. Maximum time:        21.6989s
#
# List, not reveal queue class
#   .. Mean time:           20.5513s
#   .. Median time:         20.5955s
#   .. Minimum time:        20.3295s
#   .. Maximum time:        20.8796s
#
# Local variables rather than class attributes (same as current implementation):
#   .. Mean time:           20.4755s
#   .. Median time:         20.5072s
#   .. Minimum time:        20.0755s
#   .. Maximum time:        20.9185s
# vs. actual current implementation
#   .. Mean time:           15.9727s
#   .. Median time:         16.0136s
#   .. Minimum time:        15.6708s
#   .. Maximum time:        16.2176s
#
# All tests beyong this point were done on the main implementation.
# Another control of main implementation:
#   .. Mean time:           15.8516s
#   .. Median time:         15.8356s
#   .. Minimum time:        15.7060s
#   .. Maximum time:        16.1512s
#
# Removed single-use methods to check state:
# Holy canoli! Wow, way more of an effect than I would have guessed!
#   .. Mean time:           8.4202s
#   .. Median time:         8.4140s
#   .. Minimum time:        8.3310s
#   .. Maximum time:        8.5167s
#
# Minimised self references in reveal:
#   .. Mean time:           7.2755s
#   .. Median time:         7.2363s
#   .. Minimum time:        7.0904s
#   .. Maximum time:        7.8403s
#
# Minimised self references in go:
#   .. Mean time:           7.0525s
#   .. Median time:         7.0513s
#   .. Minimum time:        7.0310s
#   .. Maximum time:        7.0904s
#
# Pass in attributes as variables each go call:
#   .. Mean time:           7.0533s
#   .. Median time:         7.0704s
#   .. Minimum time:        6.9541s
#   .. Maximum time:        7.1899s
#
# Reveal as a local function:
#   .. Mean time:           6.9708s
#   .. Median time:         6.9405s
#   .. Minimum time:        6.9298s
#   .. Maximum time:        7.0901s
#
# Reveal attribute as local (undid):
#   .. Mean time:           7.0358s
#   .. Median time:         7.0566s
#   .. Minimum time:        6.8998s
#   .. Maximum time:        7.2487s
#
# Removing asserts (negligible, undid):
#   .. Mean time:           6.9559s
#   .. Median time:         6.9324s
#   .. Minimum time:        6.8747s
#   .. Maximum time:        7.1945s
#
# Not using precomputed offsets:
# Another one I wasn't expecting! Not as impactful, though
#   .. Mean time:           6.7642s
#   .. Median time:         6.7213s
#   .. Minimum time:        6.6817s
#   .. Maximum time:        6.8835s
#
# Removing checks preventing iterating over own coordiantes:
# Bigger impact than I was expecting.
#   .. Mean time:           6.2699s
#   .. Median time:         6.2302s
#   .. Minimum time:        6.2138s
#   .. Maximum time:        6.3893s
#
# New benchmark:
# Turns out I messed up. When adding neighbours to reveal queue, I was checking bit 1
# rather than bit 3. This mistake was back in removing method calls. Hilariously, this
# wouldn't reveal mines and so wouldn't fail the assert. The only downside of this bug was that
# it performed additional reveals; previous tests are valid since optimisations didn't depend
# strongly on the affect portion, with th exception that removing method calls was
# even more effective than expected.
# Anyways, new benchmark
#   .. Mean time:           4.1314s
#   .. Median time:         4.2006s
#   .. Minimum time:        3.4819s
#   .. Maximum time:        4.5260s
#
# Using a single forloop, undoing adding to rq when nearby mine is revealed:
# Despite it doing extra work sometimes, we expect that near the critical density we will
# expect lots of zeroes, so most of the time we avoid the extra work. When we have to do the extra
# work, it will still be fast becasue the reveal count will be smaller.
#   .. Mean time:           3.0675s
#   .. Median time:         2.9905s
#   .. Minimum time:        2.6258s
#   .. Maximum time:        3.9635s
#
# Added check to minimise work to undo (undid! wheh, no!)
#   .. Mean time:           8.8203s
#   .. Median time:         8.8311s
#   .. Minimum time:        8.6347s
#   .. Maximum time:        9.0069s
#
# Only checks for mine in adjacent cell when adding new cell:
#   .. Mean time:           2.4174s
#   .. Median time:         2.3738s
#   .. Minimum time:        2.1609s
#   .. Maximum time:        2.7293s
#
# Asserts revealed cell isn't a mine (negligible):
#   .. Mean time:           2.4371s
#   .. Median time:         2.4017s
#   .. Minimum time:        2.1180s
#   .. Maximum time:        2.7422s
#
# Unpacks position prior to assert (negligible, undid):
#   .. Mean time:           2.4829s
#   .. Median time:         2.4369s
#   .. Minimum time:        2.2752s
#   .. Maximum time:        2.8116s
#
# Only sets nonzero if not already nonzero (negligible):
#   .. Mean time:           2.4676s
#   .. Median time:         2.5345s
#   .. Minimum time:        2.1335s
#   .. Maximum time:        2.6965s
#
# Reveals not as a class attribute
#   .. Mean time:           2.5160s
#   .. Median time:         2.5465s
#   .. Minimum time:        2.3364s
#   .. Maximum time:        2.6693s
#
# Reveals as decreasing cutoff
#   .. Mean time:           2.5081s
#   .. Median time:         2.5435s
#   .. Minimum time:        2.3613s
#   .. Maximum time:        2.6038s
#
# Reveals as length of RQ, RQ index rather than pop:
#   .. Mean time:           2.5260s
#   .. Median time:         2.4802s
#   .. Minimum time:        2.3466s
#   .. Maximum time:        2.7606s
#
# Silly me, reveals as index i of RQ, no pop:
#   .. Mean time:           2.4018s
#   .. Median time:         2.4190s
#   .. Minimum time:        2.2127s
#   .. Maximum time:        2.6958s
#
# Minesweeper as a function, not a class (sticking with class since difference is negligible)
#   .. Mean time:           2.4094s
#   .. Median time:         2.4331s
#   .. Minimum time:        2.0620s
#   .. Maximum time:        2.6156s
#
# Ensuring initial zero reveal by creating initial board state:
# This isn't slower, but rather more board states go to cutoff. Notice how much less
# variation between values, because it p(finite) ~ 0 while before p(finite) ~ 0.4.
#   .. Mean time:           3.7330s
#   .. Median time:         3.7138s
#   .. Minimum time:        3.7041s
#   .. Maximum time:        3.8752s
#
# One more control.
# Unforunately, I'll have to lose this time because I realised a flaw in this optimisation:
# Checking for non-zero cannot be done only when adding new neighbours, each revealed cell
# has to check for to reveal...
# Imagine two adjacent cells, A and B, where A is adjacent to a mine but not B. A is revealed 
# first and adds neighbours, all to flag 0 meaning not in reveal queue. Then B is revealed but even
# though it is zero value (not flag 4), its neighbours already exist so it cannot add them to torq.
# .. Mean time:           3.6998s
# .. Median time:         3.6935s
# .. Minimum time:        3.6896s
# .. Maximum time:        3.7275s
#
# Old reveal scheme (no temp to-reveal queue)
# .. Mean time:           5.8034s
# .. Median time:         5.8017s
# .. Minimum time:        5.7962s
# .. Maximum time:        5.8197s
#
# New reveal strategy patch
#   BAD
#
# Old reveal (now current) with visualise to false
# .. Mean time:           5.9161s
# .. Median time:         5.9258s
# .. Minimum time:        5.8797s
# .. Maximum time:        5.9788s
#
# Okay, new benchmark after a few necessary bells and whistles have been added
# .. Mean time:           6.1752s
# .. Median time:         6.1803s
# .. Minimum time:        6.2780s
# .. Maximum time:        6.0722s
