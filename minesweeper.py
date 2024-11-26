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
        self.reveal_queue: list[tuple[int]] = []

        # The board grid
        self.grid: dict[tuple[int]] = {}

        # The mine density
        self.rho = rho

        # When a reveal is considered infinite
        self.cutoff = cutoff

        # A list of offsets used to access neighbours
        self.offsets = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


        # Starting cell.
        # In modern Minesweeper, first reveal is guaranteed to be a a zero.
        # Since the point of this isn't creating a fair game but rather fidning
        # the critical density, no need to implement this.
        # That does mean the critical density is marginally higher in modern games over classic ones.
        self.add((0, 0))


    # Does the game of expand
    def go(self) -> None:

        # First reveal to populate the reveal queue
        self.grid[(0, 0)] |= 8
        self.reveal_queue.append((0, 0))

        # Keeps revealing cells until either the cutoff is reached, or no cells left to reveal
        while len(self.reveal_queue) > 0 and self.reveals < self.cutoff:
            self.reveal(self.reveal_queue.pop(0))
    

    # Adds an empty cell to the grid
    def add(self, pos: tuple[int]) -> None:

        # I will likely remove this check once everything is working.
        # This check decreases performance!
        assert pos not in self.grid, f"Cannot add cell in occupied positions b({pos[0]}, {pos[1]})"
        
        # Adds the new cell
        self.grid[pos] = self.mine()

    # Rolls a check whether or not there should be a mine
    def mine(self):
        return 2 if random() < self.rho and self.reveals > 1 else 0
    

    # Returns a list of neighbouring positions
    def neighbours(self, pos):
        x, y = pos[0], pos[1]
        return [(x + dx, y + dy) for dx, dy in self.offsets]
    


    # Reveals a grid cell, potentially expanding out to its neighbours
    def reveal(self, pos) -> None:

        # I will likely remove this check once everything is working.
        # This check decreases performance!
        assert not self.revealed(pos), f"Cell is already revealed at b({pos[0]}, {pos[1]})"

        # For near negligably faster access
        grid = self.grid

        # Reaveals the cell
        grid[pos] |= 1

        # Increments the number of reveals
        self.reveals += 1

        # Neighbours of this cell
        adj = self.neighbours(pos)
        
        # Creates new cells in unoccupied grid positions
        for u, v in adj:
                
            # Position of the neighbour
            npos = (u, v)

            # Fills unoccupied cells
            if npos not in grid:
                self.add(npos)

            # Spends the opportunity to update whether this cell has a value of zero.
            # Zeroness is tracked by bit #3
            if self.mined(npos):
                self.grid[pos] |= 4



        # Reveals neighbours if own value is zero, i.e. not third bit
        if not self.nonzeroed(pos):
            for u, v in adj:

                npos = (u, v)

                # Ensures the cell isn't already in the queue
                if not self.inrevealqueue(npos):

                    # Places item in reveal queue
                    self.grid[npos] |= 8
                    self.reveal_queue.append(npos)



    # Methods to check cell state
    def revealed(self, pos: tuple[int]) -> bool:
        return self.grid[pos] & 1 != 0
    
    def mined(self, pos: tuple[int]) -> bool:
        return self.grid[pos] & 2 != 0
    
    def nonzeroed(self, pos: tuple[int]) -> bool:
        return self.grid[pos] & 4 != 0
    
    def inrevealqueue(self, pos: tuple[int]) -> bool:
        return self.grid[pos] & 8 != 0
