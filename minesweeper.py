# An infinite board of minesweeper.

# A cell is a bitflag int E 0, 7.
#   1 = is revealed
#   2 = is mine
#   4 = at least one adjacent mine

from random import random


# rho is the density of mines, aka p(mine).
# cutoff is the number of reveals before we say "yup, that's an infinite reveal".
class Minesweeper:
    def __init__(self, rho: float, cutoff: int) -> None:
        
        # the number of reveals
        self.reveals: int = 0

        # a queue of which cells to reveal next.
        # this approach allows a radial expansion.
        # Effectively a 1d list of vectors
        self.reveal_queue: RevealQueue = RevealQueue()

        # The board grid
        self.grid: dict[dict[int]] = {}

        # The mine density
        self.rho = rho

        # When a reveal is considered infinite
        self.cutoff = cutoff


        # Starting cell.
        # In modern Minesweeper, first reveal is guaranteed to be a a zero.
        # Since the point of this isn't creating a fair game but rather fidning
        # the critical density, no need to implement this.
        # That does mean the critical density is marginally higher in modern games over classic ones.
        self.add(0, 0)


    # Does the game of expand
    def go(self) -> None:

        # First reveal to populate the reveal queue
        self.grid[0][0] |= 8
        self.reveal_queue.add(0, 0)

        # Keeps revealing cells until either the cutoff is reached, or no cells left to reveal
        while len(self.reveal_queue) > 0 and self.reveals < self.cutoff:
            self.reveal(*self.reveal_queue.pop())
    

    # Adds an empty cell to the grid
    def add(self, x: int, y: int) -> None:

        # I will likely remove this check once everything is working.
        # This check decreases performance!
        assert not self.inbounds(x, y), f"Cannot add cell in occupied positions b({x}, {y})"

        # Creates the row if it does not exist
        if x not in self.grid:
            self.grid[x] = {}
        
        # Adds the new cell
        self.grid[x][y] = self.mine()

    # Rolls a check whether or not there should be a mine
    def mine(self):
        return 2 if random() < self.rho and self.reveals > 1 else 0
    


    # Reveals a grid cell, potentially expanding out to its neighbours
    def reveal(self, x: int, y: int) -> None:

        # I will likely remove this check once everything is working.
        # This check decreases performance!
        assert not self.revealed(x, y), f"Cell is already revealed at b({x}, {y})"

        # Reaveals the cell
        self.grid[x][y] |= 1

        # Increments the number of reveals
        self.reveals += 1
        
        # Creates new cells in unoccupied grid positions
        for u in range(x - 1, x + 2):
            for v in range(y - 1, y + 2):

                # Fills unoccupied cells
                if not self.inbounds(u, v):
                    self.add(u, v)

                # Spends the opportunity to update whether the cell has a value of zero.
                # Zeroness is tracked by bit #3
                if self.mined(u, v):
                    self.grid[x][y] |= 4



        # Reveals neighbours if own value is zero, i.e. not third bit
        if not self.nonzeroed(x, y):
            for u in range(x - 1, x + 2):
                for v in range(y - 1, y + 2):

                    # No need to avoid adding own position because it will fail
                    # the is revealed check.
                    if not self.inrevealqueue(u, v):

                        # Places item in reveal queue
                        self.grid[u][v] |= 8
                        self.reveal_queue.add(u, v)




    # Checks whether given coordinates currently exist.
    def inbounds(self, x: int, y: int) -> bool:
        return x in self.grid and y in self.grid[x]

    # Methods to check cell state
    def revealed(self, x: int, y: int) -> bool:
        return self.grid[x][y] & 1 != 0
    
    def mined(self, x: int, y: int) -> bool:
        return self.grid[x][y] & 2 != 0
    
    def nonzeroed(self, x: int, y: int) -> bool:
        return self.grid[x][y] & 4 != 0
    
    def inrevealqueue(self, x: int, y: int) -> bool:
        return self.grid[x][y] & 8 != 0


                    

# A quick queue class.
# Cells are added and revealed in a queue fashion, so FIFO.
# This allows the revealed area to expand radially outward: BFS.
class RevealQueue:
    def __init__(self) -> None:
        self.q = []

    def __len__(self) -> int:
        return len(self.q)

    def add(self, x, y) -> None:

        pos = [x, y]

        if pos not in self.q:
            self.q.append(pos)

    def pop(self):
        return self.q.pop(0)